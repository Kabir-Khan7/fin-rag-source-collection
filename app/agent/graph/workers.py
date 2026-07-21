"""
Worker agents — deterministic data retrievers (no LLM).

Each worker runs known SQL queries against the Gold tables and returns raw
findings. No LLM reasoning here — for known metrics, a query is exact and
instant. This is what makes the system fast and reliable on SME hardware.
"""

"""
Worker agents — leaf level. Workers now return STRUCTURED FACTS: the exact
figures pulled from tool observations, never re-typed by the LLM. The
synthesis layer injects these verbatim so no number is ever hallucinated.
"""

from decimal import Decimal
from langchain_core.messages import SystemMessage, HumanMessage

from app.agent.graph.state import AgentState
from app.agent.graph.llm import get_llm
from app.agent.graph.finance_graph import sql_executor, strip_thinking
from app.utils.logger import get_logger

logger = get_logger(__name__)


def cashflow_worker_node(state: AgentState) -> dict:
    """
    Cash-Flow Worker. Runs SQL, returns exact figures as structured facts.
    The LLM is NOT trusted to reproduce numbers — Python owns that.
    """
    logger.info("Cash-Flow Worker activated.")

    # Deterministic query — no LLM in the numeric path.
    rows = sql_executor(
        "SELECT current_cash, avg_monthly_burn, runway_months, status "
        "FROM dbo.gold_cash_runway"
    )
    if not rows:
        return {"facts": [], "escalations": ["[Cash-Flow Worker] No runway data."]}

    row = rows[0]
    facts = [
        {
            "label": "cash_runway_months",
            "value": row["runway_months"],
            "display": f"{row['runway_months']:.1f} months",
            "source": {"table": "gold_cash_runway", "column": "runway_months"},
        },
        {
            "label": "current_cash",
            "value": row["current_cash"],
            "display": f"PKR {row['current_cash']:,.2f}",
            "source": {"table": "gold_cash_runway", "column": "current_cash"},
        },
        {
            "label": "monthly_burn",
            "value": row["avg_monthly_burn"],
            "display": f"PKR {row['avg_monthly_burn']:,.2f}",
            "source": {"table": "gold_cash_runway", "column": "avg_monthly_burn"},
        },
        {
            "label": "runway_status",
            "value": row["status"],
            "display": str(row["status"]),
            "source": {"table": "gold_cash_runway", "column": "status"},
        },
    ]
    logger.info("Cash-Flow Worker produced %d facts.", len(facts))
    return {"facts": facts}

def payables_worker(task: str) -> str:
    """
    Payables Worker: who the business owes, how much, how overdue.

    Deterministic — runs known payables-aging queries. No LLM.
    """
    logger.info("Payables Worker gathering payables data.")

    findings = []

    # Total payables + aging buckets, top vendors owed
    aging = sql_executor(
        "SELECT TOP 5 Vendor_Name, total_payable, current_0_30, "
        "days_31_60, days_61_90, days_over_90 "
        "FROM dbo.gold_payables_aging ORDER BY total_payable DESC"
    )
    findings.append(f"Top payables by vendor: {aging}")

    # Overall totals
    totals = sql_executor(
        "SELECT SUM(total_payable) AS total_owed, "
        "SUM(days_over_90) AS seriously_overdue "
        "FROM dbo.gold_payables_aging"
    )
    findings.append(f"Payables totals: {totals}")

    return "\n".join(findings)


def vendor_spend_worker(task: str) -> str:
    """
    Vendor/Spend Worker: where money goes, by vendor.

    Deterministic SQL for the numbers, plus optional semantic context from
    the vector store for narrative ("what kind of spend").
    """
    logger.info("Vendor/Spend Worker gathering spend data.")

    findings = []

    # Top vendors by spend
    top_vendors = sql_executor(
        "SELECT TOP 5 Vendor_Name, total_spend, invoice_count, avg_invoice "
        "FROM dbo.gold_vendor_spend ORDER BY total_spend DESC"
    )
    findings.append(f"Top vendors by spend: {top_vendors}")

    # Semantic context: what the spending is about (uses the vector store).
    context = vector_retriever(task, source_type="invoice")
    findings.append(f"Related invoice context: {context}")

    return "\n".join(findings)