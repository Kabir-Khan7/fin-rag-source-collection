"""
Worker agents — leaf level, deterministic data retrievers (no LLM in the
numeric path). Each returns STRUCTURED FACTS: exact figures with pre-formatted
display strings and source metadata, so no number is ever re-typed by the LLM.
"""

import json

from app.agent.graph.state import AgentState
from app.agent.tools import sql_executor
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _run_sql(query: str) -> list[dict]:
    """Run the read-only sql_executor and parse its JSON string into rows."""
    raw = sql_executor(query)            # plain function → returns a JSON string
    try:
        rows = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        logger.error("sql_executor did not return JSON rows: %s", raw)
        return []
    if not isinstance(rows, list):
        return []
    return rows


def cashflow_worker_node(state: AgentState) -> dict:
    """Cash-Flow Worker: current cash, burn, runway, status."""
    logger.info("Cash-Flow Worker activated.")
    rows = _run_sql(
        "SELECT current_cash, avg_monthly_burn, runway_months, status "
        "FROM dbo.gold_cash_runway"
    )
    if not rows:
        return {"facts": []}
    row = rows[0]
    return {"facts": [
        {"label": "cash_runway_months", "value": row["runway_months"],
         "display": f"{float(row['runway_months']):.1f} months",
         "source": {"table": "gold_cash_runway", "column": "runway_months"}},
        {"label": "current_cash", "value": row["current_cash"],
         "display": f"PKR {float(row['current_cash']):,.2f}",
         "source": {"table": "gold_cash_runway", "column": "current_cash"}},
        {"label": "monthly_burn", "value": row["avg_monthly_burn"],
         "display": f"PKR {float(row['avg_monthly_burn']):,.2f}",
         "source": {"table": "gold_cash_runway", "column": "avg_monthly_burn"}},
        {"label": "runway_status", "value": row["status"],
         "display": str(row["status"]),
         "source": {"table": "gold_cash_runway", "column": "status"}},
    ]}


def payables_worker_node(state: AgentState) -> dict:
    """Payables Worker: total owed and how much is seriously overdue."""
    logger.info("Payables Worker activated.")
    rows = _run_sql(
        "SELECT SUM(total_payable) AS total_owed, "
        "SUM(days_over_90) AS seriously_overdue "
        "FROM dbo.gold_payables_aging"
    )
    if not rows:
        return {"facts": []}
    row = rows[0]
    return {"facts": [
        {"label": "total_payables", "value": row["total_owed"],
         "display": f"PKR {float(row['total_owed']):,.2f}",
         "source": {"table": "gold_payables_aging", "column": "total_payable"}},
        {"label": "overdue_90plus", "value": row["seriously_overdue"],
         "display": f"PKR {float(row['seriously_overdue']):,.2f}",
         "source": {"table": "gold_payables_aging", "column": "days_over_90"}},
    ]}


def vendor_spend_worker_node(state: AgentState) -> dict:
    """Vendor/Spend Worker: top vendors by total spend."""
    logger.info("Vendor/Spend Worker activated.")
    rows = _run_sql(
        "SELECT TOP 5 Vendor_Name, total_spend, invoice_count, avg_invoice "
        "FROM dbo.gold_vendor_spend ORDER BY total_spend DESC"
    )
    facts = []
    for i, row in enumerate(rows, 1):
        facts.append({
            "label": f"top_vendor_{i}",
            "value": row["total_spend"],
            "display": f"{row['Vendor_Name']} — PKR {float(row['total_spend']):,.2f} "
                       f"({row['invoice_count']} invoices)",
            "source": {"table": "gold_vendor_spend", "column": "total_spend"},
        })
    return {"facts": facts}