"""
The AI CFO graph — L1, deterministic hierarchy with one surgical LLM call.

Flow: Owner -> CFO intake (routing) -> Finance HOD (deterministic retrieval)
      -> CFO synthesis (the ONE LLM call, composes the owner's answer).

Fast (one model call), reliable (no model-written SQL), and structurally
the real org chart.
"""

import sqlite3

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


def cfo_synthesis_node(state: AgentState) -> dict:
    """The one LLM call: compose the owner-facing answer from the findings."""
    logger.info("AI CFO synthesizing final answer (single LLM call).")

    escalations = state.get("escalations", [])
    findings_text = "\n".join(escalations) if escalations else "No data available."

    question = ""
    for m in state["messages"]:
        if m.type == "human":
            question = m.content
            break

    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content=CFO_SYNTHESIS_PROMPT),
        HumanMessage(content=f"Owner asked: {question}\n\nFigures:\n{findings_text}"),
    ])
    answer = strip_thinking(response.content)
    return {"final_answer": answer, "messages": [AIMessage(content=answer)]}


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