"""
ShaunMariaOS

Advisor Engine
"""

from apps.formatting_engine import money
from apps.money_engine import get_money_summary
from apps.summary_engine import get_system_summary

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

def add(advice, priority, message):
    """Add one advisor message."""
    advice.append((priority, message))


# ======================================================
# MONEY
# ======================================================

def money_advice():

    advice = []

    try:
        summary = get_money_summary()
    except Exception:
        add(
            advice,
            WARNING,
            "⚠️ Money information is unavailable."
        )
        return advice

    income = summary["income"]
    expenses = summary["expenses"]
    allocated = summary["allocated"]
    available = summary["available_money"]

    # Income

    if income <= 0:
        add(
            advice,
            WARNING,
            "💰 No income has been received this month."
        )

    # Available cash

    if available < 0:
        add(
            advice,
            CRITICAL,
            f"🚨 You are {money(abs(available))} over budget."
        )

    elif available < 300:
        add(
            advice,
            WARNING,
            f"⚠️ Only {money(available)} remains available."
        )

    elif available < 1000:
        add(
            advice,
            INFO,
            f"💰 {money(available)} remains available."
        )

    else:
        add(
            advice,
            POSITIVE,
            "✅ Your cash position looks healthy."
        )

    # Allocations

    if income > 0 and allocated > income:
        add(
            advice,
            CRITICAL,
            "🚨 Allocated funds exceed income."
        )

    # Expenses

    if income > 0:

        spending = (expenses / income) * 100

        if spending >= 90:
            add(
                advice,
                WARNING,
                f"⚠️ You've spent {spending:.1f}% of this month's income."
            )

        elif spending >= 70:
            add(
                advice,
                INFO,
                f"💳 Spending is at {spending:.1f}% this month."
            )

    return advice


# ======================================================
# WEDDING
# ======================================================

def wedding_advice(wedding):

    advice = []

    days = wedding.get("days_remaining", "-")
    shortfall = wedding.get("shortfall", 0)
    paid = wedding.get("paid_percentage", 0)

    if isinstance(days, int):

        if days <= 30:
            add(
                advice,
                CRITICAL,
                f"💍 Only {days} days until the wedding!"
            )

        elif days <= 90:
            add(
                advice,
                WARNING,
                f"💍 {days} days until the wedding."
            )

        elif days <= 180:
            add(
                advice,
                INFO,
                f"💍 {days} days remaining."
            )

    if shortfall > 0:

        add(
            advice,
            WARNING,
            f"💳 Wedding fund is short by {money(shortfall)}."
        )

    elif paid >= 100:

        add(
            advice,
            POSITIVE,
            "🎉 Wedding budget fully funded."
        )

    elif paid >= 60:

        add(
            advice,
            POSITIVE,
            f"🎉 {paid:.1f}% of the wedding budget is paid."
        )

    seats = wedding.get("seats_available")

    try:
        seats = int(seats)

        if seats <= 10:

            add(
                advice,
                WARNING,
                f"👥 Only {seats} guest seats remain."
            )

    except Exception:
        pass

    return advice


# ======================================================
# CALENDAR
# ======================================================

def calendar_advice(calendar):

    advice = []

    events = calendar.get("event_count", 0)

    if events == 0:

        add(
            advice,
            POSITIVE,
            "📅 Your calendar is clear today."
        )

    elif events <= 2:

        add(
            advice,
            INFO,
            f"📅 {events} event(s) scheduled today."
        )

    elif events <= 4:

        add(
            advice,
            WARNING,
            f"📅 Busy day with {events} events."
        )

    else:

        add(
            advice,
            CRITICAL,
            f"📅 Very busy day ({events} events)."
        )

    return advice


# ======================================================
# MAIN
# ======================================================

def get_advisor():
    """
    Returns advisor messages sorted by importance.
    """

    try:
        summary = get_system_summary()
    except Exception:

        return [
            "⚠️ Advisor unavailable."
        ]

    advice = []

    advice.extend(
        money_advice()
    )

    advice.extend(
        wedding_advice(
            summary["wedding"]
        )
    )

    advice.extend(
        calendar_advice(
            summary["calendar"]
        )
    )

    advice.sort(
        key=lambda item: item[0]
    )

    return [
        message
        for _, message in advice[:MAX_ADVICE]
    ]

def get_next_action():

    advice = get_advisor()

    if not advice:
        return "🎉 No urgent actions today."

    first = advice[0]

    if "income" in first.lower():
        return "💰 Log this month's salary."

    if "wedding" in first.lower():
        return "💍 Review the wedding budget."

    if "guest" in first.lower():
        return "👥 Finalise the remaining guest seats."

    return "✅ Review today's advisor."