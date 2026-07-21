"""
ShaunMariaOS

System Summary Engine
"""

import logging

from apps.calendar_engine import get_calendar_summary
from apps.wedding_engine import get_wedding_summary
from utils.sheet_parser import get_finance_summary

logger = logging.getLogger(__name__)


DEFAULT_FINANCE_SUMMARY = {
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


def merge_summary(defaults: dict, supplied) -> dict:
    """Merge engine output with its default fields."""

    result = defaults.copy()

    if isinstance(supplied, dict):
        result.update(supplied)

    return result


def safe_finance_summary() -> dict:
    """Load legacy finance data independently."""

    try:
        summary = get_finance_summary()

        return merge_summary(
            DEFAULT_FINANCE_SUMMARY,
            summary,
        )

    except Exception:
        logger.exception(
            "System summary could not load finance data."
        )

        return DEFAULT_FINANCE_SUMMARY.copy()


def safe_wedding_summary() -> dict:
    """Load WeddingOS data independently."""

    try:
        summary = get_wedding_summary()

        return merge_summary(
            DEFAULT_WEDDING_SUMMARY,
            summary,
        )

    except Exception:
        logger.exception(
            "System summary could not load wedding data."
        )

        return DEFAULT_WEDDING_SUMMARY.copy()


def safe_calendar_summary() -> dict:
    """Load Calendar data independently."""

    try:
        summary = get_calendar_summary()

        return merge_summary(
            DEFAULT_CALENDAR_SUMMARY,
            summary,
        )

    except Exception:
        logger.exception(
            "System summary could not load calendar data."
        )

        return DEFAULT_CALENDAR_SUMMARY.copy()


def get_system_summary() -> dict:
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
    print(get_system_summary())