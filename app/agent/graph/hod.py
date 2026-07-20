"""
Head of Department agents — deterministic routers.

The Finance HOD decides (in code) which worker(s) a task needs, calls them,
and packages their findings. No LLM call — routing by keyword/rule is
reliable and instant on any hardware.
"""

from app.agent.graph.state import AgentState
from app.agent.graph.workers import cashflow_worker
from app.utils.logger import get_logger

logger = get_logger(__name__)


def finance_hod_node(state: AgentState) -> dict:
    """
    Finance HOD: routes the task to the right worker(s), collects findings.

    L1: routes everything to the Cash-Flow Worker. L2 adds keyword-based
    routing among Cash-Flow, Payables, and Vendor/Spend workers.
    """
    question = ""
    for m in state["messages"]:
        if m.type == "human":
            question = m.content
            break

    logger.info("Finance HOD routing task: %s", question[:60])

    # Deterministic delegation (L2 will branch on keywords).
    finding = cashflow_worker(question)

    return {"escalations": [f"[Finance · Cash-Flow] {finding}"]}