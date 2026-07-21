"""
ShaunMariaOS

System Summary Engine

Combines the main operating-system summaries into one safe response.
Each engine is loaded independently so that one failure does not prevent
the remaining system data from being displayed.
"""

import logging
from typing import Any

from apps.calendar_engine import get_calendar_summary
from apps.money_engine import get_money_summary
from apps.wedding_engine import get_wedding_summary

logger = logging.getLogger(__name__)


DEFAULT_FINANCE_SUMMARY = {
    # MoneyOS field names
    "income": 0.0,
    "expenses": 0.0,
    "allocated": 0.0,
    "monthly_cash_flow": 0.0,
    "available_money": 0.0,

    # Temporary compatibility fields
    "salary": 0.0,
    "savings": 0.0,
    "bills": 0.0,
    "insurance": 0.0,
    "commitments": 0.0,
    "available": 0.0,

    "health": "⚠️ Finance unavailable",
}

DEFAULT_WEDDING_SUMMARY = {
    "days_remaining": "-",
    "guest_total": "-",
    "seats_available": "-",
    "total_budget": 0.0,
    "paid": 0.0,
    "balance": 0.0,
    "current_savings": 0.0,
    "shortfall": 0.0,
    "paid_percentage": 0.0,
}

DEFAULT_CALENDAR_SUMMARY = {
    "event_count": 0,
    "next_event": "⚠️ Calendar unavailable",
}


def merge_summary(
    defaults: dict[str, Any],
    supplied: Any,
) -> dict[str, Any]:
    """
    Merge engine output with its default fields.

    Unknown fields supplied by an engine are preserved.
    Missing fields retain their safe default values.
    """

    result = defaults.copy()

    if isinstance(supplied, dict):
        result.update(supplied)

    return result


def get_finance_health(available_money: float) -> str:
    """Return a simple status message based on available money."""

    if available_money < 0:
        return "🔴 Spending and allocations exceed received income."

    if available_money < 300:
        return "🟠 Available money is running low."

    if available_money < 1000:
        return "🟡 Available money should be monitored."

    return "🟢 Finances are currently stable."


def normalize_finance_summary(
    supplied: Any,
) -> dict[str, Any]:
    """
    Convert MoneyOS output into the common system-summary structure.

    Compatibility fields are retained temporarily while older dashboards
    are migrated from legacy Finance keys to MoneyOS keys.
    """

    summary = merge_summary(
        DEFAULT_FINANCE_SUMMARY,
        supplied,
    )

    income = float(summary.get("income") or 0.0)
    expenses = float(summary.get("expenses") or 0.0)
    allocated = float(summary.get("allocated") or 0.0)

    monthly_cash_flow = float(
        summary.get("monthly_cash_flow")
        if summary.get("monthly_cash_flow") is not None
        else income - expenses
    )

    available_money = float(
        summary.get("available_money")
        if summary.get("available_money") is not None
        else monthly_cash_flow - allocated
    )

    # Official MoneyOS fields
    summary["income"] = income
    summary["expenses"] = expenses
    summary["allocated"] = allocated
    summary["monthly_cash_flow"] = monthly_cash_flow
    summary["available_money"] = available_money

    # Temporary aliases for modules still using the legacy schema
    summary["salary"] = income
    summary["commitments"] = allocated
    summary["available"] = available_money

    summary["health"] = get_finance_health(
        available_money
    )

    return summary


def safe_finance_summary() -> dict[str, Any]:
    """Load MoneyOS data independently."""

    try:
        summary = get_money_summary()

        return normalize_finance_summary(summary)

    except Exception:
        logger.exception(
            "System summary could not load MoneyOS data."
        )

        return DEFAULT_FINANCE_SUMMARY.copy()


def safe_wedding_summary() -> dict[str, Any]:
    """Load WeddingOS data independently."""

    try:
        summary = get_wedding_summary()

        return merge_summary(
            DEFAULT_WEDDING_SUMMARY,
            summary,
        )

    except Exception:
        logger.exception(
            "System summary could not load WeddingOS data."
        )

        return DEFAULT_WEDDING_SUMMARY.copy()


def safe_calendar_summary() -> dict[str, Any]:
    """Load CalendarOS data independently."""

    try:
        summary = get_calendar_summary()

        return merge_summary(
            DEFAULT_CALENDAR_SUMMARY,
            summary,
        )

    except Exception:
        logger.exception(
            "System summary could not load CalendarOS data."
        )

        return DEFAULT_CALENDAR_SUMMARY.copy()


def get_system_summary() -> dict[str, dict[str, Any]]:
    """
    Return all main system summaries.

    Failure in one engine does not erase data from the others.
    """

    return {
        "finance": safe_finance_summary(),
        "wedding": safe_wedding_summary(),
        "calendar": safe_calendar_summary(),
    }


if __name__ == "__main__":
    from pprint import pprint

    pprint(get_system_summary())