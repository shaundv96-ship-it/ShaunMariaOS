"""
ShaunMariaOS

Dashboard Engine
"""

import logging
from typing import Any

from app_config import (
    APP_NAME,
    APP_STAGE,
    APP_VERSION,
    HOME_NAME,
    HOME_TOP,
)
from apps.advisor_engine import get_advisor, get_next_action
from apps.formatting_engine import money
from apps.greeting_engine import get_greeting
from apps.money_engine import get_money_summary
from apps.summary_engine import get_system_summary
from utils.time import sg_now
from utils.ui import build_screen
from utils.widgets import info_widget, metric_widget


logger = logging.getLogger(__name__)

VERSION = f"v{APP_VERSION} {APP_STAGE}"


# ==========================================================
# Default fallback data
# ==========================================================

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

DEFAULT_MONEY_SUMMARY = {
    "income": 0.0,
    "expenses": 0.0,
    "allocated": 0.0,
    "monthly_cash_flow": 0.0,
    "available_money": 0.0,
}


# ==========================================================
# Helpers
# ==========================================================

def safe_number(
    value: Any,
    default: float = 0.0,
) -> float:
    """Convert a value into a float safely."""

    try:
        if value in (None, "", "-"):
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def merge_summary(
    defaults: dict,
    supplied: Any,
) -> dict:
    """Merge engine data with fallback values."""

    result = defaults.copy()

    if isinstance(supplied, dict):
        result.update(supplied)

    return result


# ==========================================================
# Safe engine wrappers
# ==========================================================

def safe_system_summary() -> dict:
    """Load the system summary without crashing the dashboard."""

    fallback = {
        "finance": DEFAULT_FINANCE_SUMMARY.copy(),
        "wedding": DEFAULT_WEDDING_SUMMARY.copy(),
        "calendar": DEFAULT_CALENDAR_SUMMARY.copy(),
    }

    try:
        summary = get_system_summary()

        if not isinstance(summary, dict):
            logger.error(
                "System summary returned an invalid value: %r",
                summary,
            )
            return fallback

        return {
            "finance": merge_summary(
                DEFAULT_FINANCE_SUMMARY,
                summary.get("finance"),
            ),
            "wedding": merge_summary(
                DEFAULT_WEDDING_SUMMARY,
                summary.get("wedding"),
            ),
            "calendar": merge_summary(
                DEFAULT_CALENDAR_SUMMARY,
                summary.get("calendar"),
            ),
        }

    except Exception:
        logger.exception(
            "Dashboard could not load the system summary."
        )
        return fallback


def safe_money_summary() -> dict:
    """Load MoneyOS without crashing the dashboard."""

    try:
        summary = get_money_summary()

        if not isinstance(summary, dict):
            logger.error(
                "MoneyOS returned an invalid value: %r",
                summary,
            )
            return DEFAULT_MONEY_SUMMARY.copy()

        return merge_summary(
            DEFAULT_MONEY_SUMMARY,
            summary,
        )

    except Exception:
        logger.exception(
            "Dashboard could not load MoneyOS."
        )
        return DEFAULT_MONEY_SUMMARY.copy()


def safe_advice() -> str:
    """Load and format AdvisorOS messages safely."""

    try:
        advice = get_advisor()

    except Exception:
        logger.exception(
            "Dashboard could not load AdvisorOS."
        )
        return "⚠️ Advisor temporarily unavailable."

    if not advice:
        return "🎉 Everything looks good today."

    if isinstance(advice, str):
        return advice

    if not isinstance(advice, (list, tuple)):
        logger.error(
            "AdvisorOS returned an invalid value: %r",
            advice,
        )
        return "⚠️ Advisor temporarily unavailable."

    messages = [
        str(item).strip()
        for item in advice
        if str(item).strip()
    ]

    if not messages:
        return "🎉 Everything looks good today."

    return "\n".join(
        f"{index}. {message}"
        for index, message in enumerate(
            messages[:5],
            start=1,
        )
    )


def safe_next_action() -> str:
    """Load today's recommended action safely."""

    try:
        action = get_next_action()

        if not action:
            return "✅ Review today's priorities."

        return str(action)

    except Exception:
        logger.exception(
            "Dashboard could not load today's action."
        )
        return "⚠️ Today's action is temporarily unavailable."


def safe_greeting() -> str:
    """Load the greeting safely."""

    try:
        greeting = get_greeting()

        if greeting:
            return str(greeting)

    except Exception:
        logger.exception(
            "Dashboard could not load the greeting."
        )

    return "Good morning Shaun & Maria"


# ==========================================================
# Dashboard
# ==========================================================

def get_dashboard_message() -> str:
    """Build the main ShaunMariaOS dashboard."""

    summary = safe_system_summary()
    money_summary = safe_money_summary()

    wedding = summary["wedding"]
    calendar = summary["calendar"]

    today = sg_now().strftime(
        "%A, %d %B %Y"
    )

    wedding_days = wedding.get(
        "days_remaining",
        "-",
    )

    guest_total = wedding.get(
        "guest_total",
        "-",
    )

    paid_percentage = safe_number(
        wedding.get("paid_percentage"),
    )

    wedding_balance = safe_number(
        wedding.get("balance"),
    )

    income = safe_number(
        money_summary.get("income"),
    )

    expenses = safe_number(
        money_summary.get("expenses"),
    )

    allocated = safe_number(
        money_summary.get("allocated"),
    )

    available_money = safe_number(
        money_summary.get("available_money"),
    )

    next_event = calendar.get(
        "next_event",
        "⚠️ Calendar unavailable",
    )

    if not next_event:
        next_event = "No events scheduled today."

    sections = [
        info_widget(
            "👋 Greeting",
            f"{safe_greeting()}\n"
            f"📅 {today}",
        ),

        metric_widget(
            "💍 Wedding",
            f"{wedding_days} days remaining\n"
            f"Guests: {guest_total}\n"
            f"Budget: {paid_percentage:.1f}% paid\n"
            f"Balance: {money(wedding_balance)}",
        ),

        metric_widget(
            "💰 Money",
            f"Income received: {money(income)}\n"
            f"Spent: {money(expenses)}\n"
            f"Allocated: {money(allocated)}\n"
            f"Available to spend: {money(available_money)}",
        ),

        info_widget(
            "📅 Today",
            str(next_event),
        ),

        info_widget(
            "🏠 Home",
            f"{HOME_NAME}\n"
            f"Status: Booked ✅\n"
            f"TOP: {HOME_TOP}",
        ),

        info_widget(
            "🧠 Advisor",
            safe_advice(),
        ),

        info_widget(
            "⚡ Today's Action",
            safe_next_action(),
        ),
    ]

    return build_screen(
        f"❤️ <b>{APP_NAME}</b>",
        sections,
        VERSION,
    )


# ==========================================================
# Local test
# ==========================================================

if __name__ == "__main__":
    print(get_dashboard_message())