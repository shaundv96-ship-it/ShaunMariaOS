"""
ShaunMariaOS

Advisor Engine
"""

from apps.summary_engine import get_system_summary


def get_advisor():
    summary = get_system_summary()

    finance = summary["finance"]
    wedding = summary["wedding"]
    calendar = summary["calendar"]

    advice = []

    # -----------------------------
    # Finance
    # -----------------------------

    if finance["available"] >= 1000:
        advice.append(
            "💰 You have healthy available cash this month."
        )
    elif finance["available"] >= 500:
        advice.append(
            "💰 Cash flow looks manageable."
        )
    else:
        advice.append(
            "⚠️ Watch spending this month."
        )

    # -----------------------------
    # Wedding
    # -----------------------------

    if wedding["days_remaining"] <= 120:
        advice.append(
            f"💍 Only {wedding['days_remaining']} days until the wedding."
        )

    if wedding["paid_percentage"] >= 60:
        advice.append(
            f"🎉 {wedding['paid_percentage']:.1f}% of your wedding budget has been paid."
        )

    if str(wedding["seats_available"]).isdigit():
        seats = int(wedding["seats_available"])

        if seats <= 10:
            advice.append(
                f"👥 Only {seats} guest seats remain."
            )

    # -----------------------------
    # Calendar
    # -----------------------------

    if calendar["event_count"] == 0:
        advice.append(
            "📅 No meetings scheduled today."
        )

    return advice