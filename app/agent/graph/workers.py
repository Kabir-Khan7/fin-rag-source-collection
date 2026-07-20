"""
Worker agents — deterministic data retrievers (no LLM).

Each worker runs known SQL queries against the Gold tables and returns raw
findings. No LLM reasoning here — for known metrics, a query is exact and
instant. This is what makes the system fast and reliable on SME hardware.
"""

from app.agent.tools import sql_executor
from app.utils.logger import get_logger

logger = get_logger(__name__)


def cashflow_worker(task: str) -> str:
    """
    Cash-Flow Worker: retrieves all cash-health metrics deterministically.

    Runs the known cash queries and returns a compact findings string for
    the manager/HOD to pass upward. No LLM call.
    """
    logger.info("Cash-Flow Worker (deterministic) gathering cash metrics.")

    findings = []

    # Cash runway
    runway = sql_executor(
        "SELECT current_cash, avg_monthly_burn, runway_months, status "
        "FROM dbo.gold_cash_runway"
    )
    findings.append(f"Cash runway: {runway}")

    # Cash position
    position = sql_executor(
        "SELECT current_balance, as_of_date, total_inflow, total_outflow "
        "FROM dbo.gold_cash_position"
    )
    findings.append(f"Cash position: {position}")

    return "\n".join(findings)