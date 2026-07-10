"""
ShaunMariaOS

Insight Engine
"""

from apps.finance_engine import get_finance_summary
from apps.wedding_engine import get_wedding_summary
from apps.calendar_engine import get_calendar_summary


def build_insights():
    finance = get_finance_summary()
    wedding = get_wedding_summary()
    calendar = get_calendar_summary()

    insights = []

    # ------------------------
    # Finance
    # ------------------------

    if finance["available"] >= 1500:
        insights.append(
            "💰 Excellent cash position this month."
        )

    elif finance["available"] >= 1000:
        insights.append(
            "💰 Cash flow is healthy."
        )

    elif finance["available"] >= 500:
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

    if wedding["days_remaining"] <= 120:
        insights.append(
            f"💒 Wedding is only {wedding['days_remaining']} days away."
        )

    if wedding["paid_percentage"] >= 70:
        insights.append(
            "✅ Wedding budget is mostly funded."
        )

    elif wedding["paid_percentage"] >= 40:
        insights.append(
            "💍 Wedding budget is progressing well."
        )

    # ------------------------
    # Guests
    # ------------------------

    try:
        seats = int(wedding["seats_available"])
        if seats <= 10:
            insights.append(
                "🎉 Guest list is almost full."
            )
    except:
        pass

    # ------------------------
    # Calendar
    # ------------------------

    if calendar["event_count"] == 0:
        insights.append(
            "📅 No meetings scheduled today."
        )

    return insights