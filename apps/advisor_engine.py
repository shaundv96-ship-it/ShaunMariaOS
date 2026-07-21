"""
ShaunMariaOS

Advisor Engine
"""

import logging
from typing import Any

from apps.formatting_engine import money
from apps.money_engine import get_money_summary
from apps.summary_engine import get_system_summary


logger = logging.getLogger(__name__)


# ======================================================
# PRIORITIES
# ======================================================

CRITICAL = 1
WARNING = 2
INFO = 3
POSITIVE = 4

MAX_ADVICE = 5


# ======================================================
# HELPERS
# ======================================================

def add(
    advice: list[tuple[int, str]],
    priority: int,
    message: str,
) -> None:
    """Add one AdvisorOS message."""

    advice.append((priority, message))


def safe_number(
    value: Any,
    default: float = 0.0,
) -> float:
    """Convert a value to float safely."""

    try:
        if value in (None, "", "-"):
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


# ======================================================
# MONEY
# ======================================================

def money_advice() -> list[tuple[int, str]]:
    """Generate advice from MoneyOS."""

    advice = []

    try:
        summary = get_money_summary()

    except Exception:
        logger.exception(
            "AdvisorOS could not load MoneyOS."
        )

        add(
            advice,
            WARNING,
            "⚠️ Money information is unavailable.",
        )

        return advice

    if not isinstance(summary, dict):
        logger.error(
            "MoneyOS returned an unexpected value: %r",
            summary,
        )

        add(
            advice,
            WARNING,
            "⚠️ Money information is unavailable.",
        )

        return advice

    income = safe_number(
        summary.get("income"),
    )

    expenses = safe_number(
        summary.get("expenses"),
    )

    allocated = safe_number(
        summary.get("allocated"),
    )

    available = safe_number(
        summary.get("available_money"),
    )

    # Income

    if income <= 0:
        add(
            advice,
            WARNING,
            "💰 No income has been received this month.",
        )

    # Available cash

    if available < 0:
        add(
            advice,
            CRITICAL,
            f"🚨 You are {money(abs(available))} over budget.",
        )

    elif available < 300:
        add(
            advice,
            WARNING,
            f"⚠️ Only {money(available)} remains available.",
        )

    elif available < 1000:
        add(
            advice,
            INFO,
            f"💰 {money(available)} remains available.",
        )

    else:
        add(
            advice,
            POSITIVE,
            "✅ Your cash position looks healthy.",
        )

    # Allocations

    if income > 0 and allocated > income:
        add(
            advice,
            CRITICAL,
            "🚨 Allocated funds exceed income.",
        )

    # Expenses

    if income > 0:
        spending_percentage = (
            expenses / income
        ) * 100

        if spending_percentage >= 90:
            add(
                advice,
                WARNING,
                (
                    "⚠️ You've spent "
                    f"{spending_percentage:.1f}% "
                    "of this month's income."
                ),
            )

        elif spending_percentage >= 70:
            add(
                advice,
                INFO,
                (
                    "💳 Spending is at "
                    f"{spending_percentage:.1f}% "
                    "this month."
                ),
            )

    return advice


# ======================================================
# WEDDING
# ======================================================

def wedding_advice(
    wedding: dict,
) -> list[tuple[int, str]]:
    """Generate advice from wedding data."""

    advice = []

    if not isinstance(wedding, dict):
        add(
            advice,
            WARNING,
            "⚠️ Wedding information is unavailable.",
        )
        return advice

    days_value = wedding.get(
        "days_remaining",
        "-",
    )

    shortfall = safe_number(
        wedding.get("shortfall"),
    )

    paid_percentage = safe_number(
        wedding.get("paid_percentage"),
    )

    try:
        days = int(days_value)

    except (TypeError, ValueError):
        days = None

    if days is not None:
        if days <= 30:
            add(
                advice,
                CRITICAL,
                f"💍 Only {days} days until the wedding!",
            )

        elif days <= 90:
            add(
                advice,
                WARNING,
                f"💍 {days} days until the wedding.",
            )

        elif days <= 180:
            add(
                advice,
                INFO,
                f"💍 {days} days remaining.",
            )

    if shortfall > 0:
        add(
            advice,
            WARNING,
            (
                "💳 Wedding fund is short by "
                f"{money(shortfall)}."
            ),
        )

    elif paid_percentage >= 100:
        add(
            advice,
            POSITIVE,
            "🎉 Wedding budget fully funded.",
        )

    elif paid_percentage >= 60:
        add(
            advice,
            POSITIVE,
            (
                f"🎉 {paid_percentage:.1f}% of the "
                "wedding budget is paid."
            ),
        )

    seats_value = wedding.get(
        "seats_available",
    )

    try:
        seats = int(seats_value)

        if 0 <= seats <= 10:
            add(
                advice,
                WARNING,
                f"👥 Only {seats} guest seats remain.",
            )

    except (TypeError, ValueError):
        pass

    return advice


# ======================================================
# CALENDAR
# ======================================================

def calendar_advice(
    calendar: dict,
) -> list[tuple[int, str]]:
    """Generate advice from today's calendar."""

    advice = []

    if not isinstance(calendar, dict):
        add(
            advice,
            WARNING,
            "⚠️ Calendar information is unavailable.",
        )
        return advice

    next_event = str(
        calendar.get("next_event", "")
    ).lower()

    if "unavailable" in next_event:
        add(
            advice,
            WARNING,
            "⚠️ Calendar information is unavailable.",
        )
        return advice

    events = int(
        safe_number(
            calendar.get("event_count"),
        )
    )

    if events == 0:
        add(
            advice,
            POSITIVE,
            "📅 Your calendar is clear today.",
        )

    elif events <= 2:
        add(
            advice,
            INFO,
            f"📅 {events} event(s) scheduled today.",
        )

    elif events <= 4:
        add(
            advice,
            WARNING,
            f"📅 Busy day with {events} events.",
        )

    else:
        add(
            advice,
            CRITICAL,
            f"📅 Very busy day ({events} events).",
        )

    return advice


# ======================================================
# MAIN ADVISOR
# ======================================================

def get_advisor() -> list[str]:
    """
    Return AdvisorOS messages sorted by importance.
    """

    try:
        summary = get_system_summary()

    except Exception:
        logger.exception(
            "AdvisorOS failed while loading the system summary."
        )

        return [
            "⚠️ Advisor information is temporarily unavailable."
        ]

    if not isinstance(summary, dict):
        logger.error(
            "System summary returned an unexpected value: %r",
            summary,
        )

        return [
            "⚠️ Advisor information is temporarily unavailable."
        ]

    advice: list[tuple[int, str]] = []

    advice.extend(
        money_advice()
    )

    advice.extend(
        wedding_advice(
            summary.get("wedding", {}),
        )
    )

    advice.extend(
        calendar_advice(
            summary.get("calendar", {}),
        )
    )

    advice.sort(
        key=lambda item: item[0]
    )

    return [
        message
        for _, message in advice[:MAX_ADVICE]
    ]


# ======================================================
# TODAY'S ACTION
# ======================================================

def get_next_action() -> str:
    """Return one practical action based on top advice."""

    try:
        advice = get_advisor()

    except Exception:
        logger.exception(
            "AdvisorOS failed while selecting today's action."
        )

        return "⚠️ Today's action is temporarily unavailable."

    if not advice:
        return "🎉 No urgent actions today."

    first = advice[0]
    first_lower = first.lower()

    if "unavailable" in first_lower:
        return "🔄 Check the system connection and logs."

    if "over budget" in first_lower:
        return "💳 Review today's spending and reduce non-essential expenses."

    if "income" in first_lower:
        return "💰 Log this month's salary."

    if "allocated funds" in first_lower:
        return "📊 Review your monthly allocations."

    if "wedding fund" in first_lower:
        return "💍 Review the wedding savings plan."

    if "wedding" in first_lower:
        return "💍 Review the next wedding priority."

    if "guest seats" in first_lower:
        return "👥 Finalise the remaining guest seats."

    if "busy day" in first_lower:
        return "📅 Review today's schedule and priorities."

    return "✅ Review today's advisor."