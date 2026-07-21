"""
The AI CFO graph — L1, deterministic hierarchy with one surgical LLM call.

Flow: Owner -> CFO intake (routing) -> Finance HOD (deterministic retrieval)
      -> CFO synthesis (the ONE LLM call, composes the owner's answer).

Fast (one model call), reliable (no model-written SQL), and structurally
the real org chart.
"""

import sqlite3
import re
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from app.agent.graph.state import AgentState
from app.agent.graph.llm import get_llm
from app.agent.graph.hod import finance_hod_node
from app.agent.graph.finance_graph import strip_thinking
from app.utils.logger import get_logger

logger = get_logger(__name__)


CFO_SYNTHESIS_PROMPT = """You are the AI CFO speaking directly to the business \
owner. Below are exact figures gathered by your finance team from the company's \
books. Turn them into one clear, concise, helpful answer to the owner's question.

Rules:
- Use ONLY the numbers provided. Never invent figures.
- Speak warmly and plainly, like a trusted CFO. One unified voice.
- Do NOT mention your internal team, tables, or process.
- If the figures signal risk (e.g., very low runway), note it briefly and \
constructively."""


def cfo_intake_node(state: AgentState) -> dict:
    """CFO intake. L1: always finance. (L2+: choose the right HOD here.)"""
    logger.info("AI CFO intake — routing to Finance.")
    return {}


CFO_SYNTHESIS_PROMPT = """You are the AI CFO speaking directly to the business \
owner. Below are the ONLY facts you may state, each with a placeholder token.

RULES:
- Refer to every figure ONLY by its {placeholder_token}. Never write a raw \
number yourself — the system fills tokens with exact values.
- Write in a clear, professional executive tone. No emojis. No filler \
greetings. Lead with the answer.
- If a figure you'd need has no token below, do not invent it — omit it.

Available facts:
{facts_block}

Write the owner's answer using the placeholder tokens."""


def cfo_synthesis_node(state: AgentState) -> dict:
    logger.info("AI CFO — synthesizing (placeholder-injection mode).")
    facts = state.get("facts", [])

    if not facts:
        return {"messages": [AIMessage(content="I couldn't gather the data for that. Could you rephrase?")]}

    # Build the fact menu the LLM sees — tokens + human labels, NO trust in it to copy numbers.
    facts_block = "\n".join(
        f"  {{{f['label']}}} = {f['display']}  (from {f['source']['table']}.{f['source']['column']})"
        for f in facts
    )

    llm = get_llm()
    prompt = CFO_SYNTHESIS_PROMPT.format(facts_block=facts_block)
    raw = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=state["messages"][-1].content),
    ])
    narrative = strip_thinking(raw.content)

    # DETERMINISTIC INJECTION — Python owns every number.
    lookup = {f["label"]: f["display"] for f in facts}
    def _sub(m):
        token = m.group(1)
        if token not in lookup:
            logger.warning("LLM referenced unknown token {%s} — left visible.", token)
            return m.group(0)  # leave "{bad_token}" in text so it's caught, not silently wrong
        return lookup[token]

    answer = re.sub(r"\{(\w+)\}", _sub, narrative)

    # Provenance footer — satisfies your architecture's source-attribution mandate.
    sources = sorted({f"{f['source']['table']}.{f['source']['column']}" for f in facts})
    answer += "\n\n— Sourced from: " + ", ".join(sources)

    return {"messages": [AIMessage(content=answer)]}


def build_cfo_graph():
    """Compile the L1 deterministic CFO hierarchy."""
    graph = StateGraph(AgentState)

    graph.add_node("cfo_intake", cfo_intake_node)
    graph.add_node("finance_hod", finance_hod_node)
    graph.add_node("cfo_synthesis", cfo_synthesis_node)

    graph.add_edge(START, "cfo_intake")
    graph.add_edge("cfo_intake", "finance_hod")
    graph.add_edge("finance_hod", "cfo_synthesis")
    graph.add_edge("cfo_synthesis", END)

    conn = sqlite3.connect("agent_memory.db", check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    return graph.compile(checkpointer=checkpointer)