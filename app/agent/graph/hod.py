"""
Head of Department agents — deterministic keyword routers.

The Finance HOD inspects the question and routes to the right worker(s).
Routing by keyword is instant and reliable — no LLM call. For broad
questions ("how's my business?"), it runs ALL workers for a full picture.
"""

from app.agent.graph.state import AgentState
from app.agent.graph.workers import (
    cashflow_worker_node,
    payables_worker_node,
    vendor_spend_worker_node,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Keyword → worker routing map.
CASHFLOW_KEYWORDS = ["cash", "runway", "burn", "balance", "liquid", "money left",
                     "income", "expense", "profit", "loss", "monthly"]
PAYABLES_KEYWORDS = ["owe", "payable", "due", "overdue", "bill", "creditor",
                     "pay", "aging", "outstanding"]
VENDOR_KEYWORDS = ["spend", "spent", "vendor", "supplier", "cost", "where",
                   "expense", "purchase", "invoice"]

# Broad questions that should gather everything.
OVERVIEW_KEYWORDS = ["how's my business", "how is my business", "overview",
                     "financial health", "how are we doing", "summary",
                     "how's the company", "overall"]


def finance_hod_node(state: AgentState) -> dict:
    """Routes by keyword, collects structured facts from each relevant worker."""
    question = ""
    for m in state["messages"]:
        if m.type == "human":
            question = m.content
            break

    q = question.lower()
    logger.info("Finance HOD routing: %s", question[:60])

    facts = []
    is_overview = any(k in q for k in OVERVIEW_KEYWORDS)

    if is_overview or any(k in q for k in CASHFLOW_KEYWORDS):
        facts += cashflow_worker_node(state).get("facts", [])
    if is_overview or any(k in q for k in PAYABLES_KEYWORDS):
        facts += payables_worker_node(state).get("facts", [])
    if is_overview or any(k in q for k in VENDOR_KEYWORDS):
        facts += vendor_spend_worker_node(state).get("facts", [])

    if not facts:
        logger.info("No keyword match — defaulting to Cash-Flow Worker.")
        facts += cashflow_worker_node(state).get("facts", [])

    logger.info("Finance HOD gathered %d fact(s).", len(facts))
    return {"facts": facts}