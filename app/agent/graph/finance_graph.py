"""
L0 — the existing ReAct loop, re-expressed as a LangGraph StateGraph.

Two nodes: an agent node (the model, with tools bound) and a tool node
(executes tool calls). A deterministic edge decides whether to loop back
to the agent or finish — with a hard iteration cap in code, not prompt.
"""

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

from langchain_core.tools import tool

from app.agent.graph.state import AgentState
from app.agent.graph.llm import get_llm
from app.agent.tools import sql_executor as _sql_executor
from app.agent.tools import vector_retriever as _vector_retriever
from app.agent.schema_context import GOLD_SCHEMA_DESCRIPTION
from app.utils.logger import get_logger


import re


def strip_thinking(text: str) -> str:
    """Remove Qwen3 <think>...</think> blocks from output text."""
    if not text:
        return text
    # Remove complete <think>...</think> blocks.
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    # Remove a dangling </think> (when the opening tag was suppressed but
    # the closing tag and preamble still render, as in your output).
    if "</think>" in cleaned:
        cleaned = cleaned.split("</think>")[-1]
    return cleaned.strip()

logger = get_logger(__name__)

MAX_ITERATIONS = 5


# Wrap your existing tool functions as LangChain tools.
@tool
def sql_executor(query: str) -> str:
    """Run a read-only SQL SELECT for exact numbers from the gold_* tables."""
    return _sql_executor(query)


@tool
def vector_retriever(query: str, source_type: str | None = None) -> str:
    """Semantic search over invoices/transactions for meaning-based questions."""
    return _vector_retriever(query, source_type)


TOOLS = [sql_executor, vector_retriever]

SYSTEM_PROMPT = f"""You are an AI CFO assistant for a small business. Answer \
financial questions using ONLY your tools — never invent numbers.

Use sql_executor for exact figures. Use vector_retriever for meaning-based lookups.

{GOLD_SCHEMA_DESCRIPTION}

Give clear, concise answers with real numbers from tool results."""


def agent_node(state: AgentState) -> dict:
    """The reasoning node: the model decides to call a tool or answer."""
    llm_with_tools = get_llm().bind_tools(TOOLS)

    # Prepend the system prompt on the first turn.
    messages = state["messages"]
    if not any(m.type == "system" for m in messages):
        from langchain_core.messages import SystemMessage
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    response = llm_with_tools.invoke(messages)
    iteration = state.get("iteration", 0) + 1
    logger.info("Agent node — iteration %d", iteration)
    return {"messages": [response], "iteration": iteration}


def should_continue(state: AgentState) -> str:
    """
    Deterministic router: loop to tools, or finish.
    Iteration cap enforced HERE in code, never in the prompt.
    """
    last = state["messages"][-1]

    # Safety cap — stop regardless of what the model wants.
    if state.get("iteration", 0) >= MAX_ITERATIONS:
        logger.warning("Hit iteration cap — ending.")
        return END

    # If the model called tools, go run them; else we're done.
    if getattr(last, "tool_calls", None):
        return "tools"
    return END


def build_finance_graph():
    """Compile the L0 finance graph."""
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(TOOLS))

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    # SqliteSaver: local, survives restarts (working memory / HITL later).
    # Build from a real connection (check_same_thread=False so it works
    # across LangGraph's execution). from_conn_string returns a context
    # manager, so we construct the saver directly instead.
    conn = sqlite3.connect("agent_memory.db", check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    return graph.compile(checkpointer=checkpointer)