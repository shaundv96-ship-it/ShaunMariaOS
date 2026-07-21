"""
ShaunMariaOS

Insight Engine
"""

from apps.calendar_engine import get_calendar_summary
from apps.money_engine import get_money_summary
from apps.wedding_engine import get_wedding_summary


def build_insights():
    """Build insights across MoneyOS, WeddingOS, and CalendarOS."""

    finance = get_money_summary()
    wedding = get_wedding_summary()
    calendar = get_calendar_summary()

    insights = []

    # ------------------------
    # Finance
    # ------------------------

    available = finance.get("available_money", 0.0)

    if available >= 1500:
        insights.append(
            "💰 Excellent cash position this month."
        )

    elif available >= 1000:
        insights.append(
            "💰 Cash flow is healthy."
        )

    elif available >= 500:
        insights.append(
            "⚠️ Watch discretionary spending."
        )

    else:
        insights.append(
            "🚨 Cash flow is tight this month."
        )

    # ------------------------
    # Wedding
    # ------------------------

    days_remaining = wedding.get("days_remaining", 0)
    paid_percentage = wedding.get("paid_percentage", 0.0)

    if days_remaining <= 120:
        insights.append(
            f"💍 Wedding is only {days_remaining} days away."
        )

    if paid_percentage >= 70:
        insights.append(
            "✅ Wedding budget is mostly funded."
        )

    elif paid_percentage >= 40:
        insights.append(
            "💒 Wedding budget is progressing well."
        )

    # ------------------------
    # Guests
    # ------------------------

    try:
        seats = int(wedding.get("seats_available", 0))

        if seats <= 10:
            insights.append(
                "🎉 Guest list is almost full."
            )

    except (TypeError, ValueError):
        pass

    # ------------------------
    # Calendar
    # ------------------------

    if calendar.get("event_count", 0) == 0:
        insights.append(
            "📅 No meetings scheduled today."
        )

    return insights
    