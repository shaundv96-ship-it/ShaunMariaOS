"""
ShaunMariaOS

Evening Wrap Engine
"""

from calendar import monthrange

from apps.calendar_engine import (
    get_event_display_time,
    get_tomorrow_events,
)
from apps.formatting_engine import money
from apps.life_engine import get_life_snapshot
from apps.reflection_engine import get_reflection

DIVIDER = "━━━━━━━━━━━━━━━━━━"


def build_tomorrow_section(events):
    """Return tomorrow's schedule text and a short closing line."""

    if not events:
        return (
            "No events scheduled.",
            "Enjoy the breathing room.",
        )

    event_lines = []

    for event in events[:5]:
        title = event.get("summary", "Untitled Event")
        event_time = get_event_display_time(event)

        event_lines.append(
            f"• {event_time} — {title}"
        )

    if len(events) > 5:
        remaining = len(events) - 5
        event_lines.append(
            f"• Plus {remaining} more event"
            f"{'s' if remaining != 1 else ''}"
        )

    closing = (
        "Tomorrow looks busy, so a little preparation may help."
        if len(events) >= 3
        else "You’re all set for tomorrow."
    )

    return "\n".join(event_lines), closing


def build_money_section(finance):
    """Return a calm, readable MoneyOS summary."""

    income = finance.get("income", 0)
    expenses = finance.get("expenses", 0)
    available = finance.get("available", 0)

    if income <= 0 and available < 0:
        return (
            f"• Spending this month: {money(expenses)}\n"
            "• Salary has not been logged yet.\n\n"
            "Your balance will update once your income is recorded."
        )

    if available < 0:
        return (
            f"• Available balance: {money(available)}\n"
            f"• Spending this month: {money(expenses)}\n\n"
            "It may be worth checking your recent spending and allocations."
        )

    if expenses <= 0:
        return (
            "No spending has been recorded this month.\n\n"
            "MoneyOS is looking steady."
        )

    return (
        f"• Spending this month: {money(expenses)}\n"
        f"• Available balance: {money(available)}"
    )


def build_wedding_section(wedding):
    """Return the current wedding countdown and funding progress."""

    days_remaining = wedding.get("days_remaining", 0)
    paid_percentage = wedding.get("paid_percentage", 0)

    if days_remaining < 0:
        return "The wedding may be over, but the adventure continues ❤️"

    if days_remaining == 0:
        return "Today is your wedding day ❤️"

    return (
        f"{days_remaining} days to go.\n\n"
        f"You’re already {paid_percentage:.0f}% funded.\n\n"
        "Another day closer ❤️"
    )


def build_closing_section(
    today,
    tomorrow_events,
):
    """Return a context-aware nightly closing."""

    last_day_of_month = monthrange(
        today.year,
        today.month,
    )[1]

    is_payday_today = today.day == last_day_of_month
    is_payday_tomorrow = today.day + 1 == last_day_of_month

    if is_payday_tomorrow:
        return (
            "Tomorrow is payday.\n\n"
            "Remember to record your salary once it comes in."
        )

    if is_payday_today:
        return (
            "Today is payday.\n\n"
            "Once your salary is recorded, MoneyOS will update automatically."
        )

    if not tomorrow_events:
        return (
            "Tomorrow looks quiet."
        )

    if len(tomorrow_events) >= 3:
        return (
            "Tomorrow looks busy.\n\n"
            "A little preparation tonight may make things easier."
        )

    return (
        "Tomorrow is already planned.\n\n"
        "You can switch off for the night."
    )


def get_evening_wrap():
    """Build the nightly Evening Wrap."""

    life = get_life_snapshot()

    finance = life["finance"]
    wedding = life["wedding"]
    today = life["generated_at"].date()

    tomorrow_events = get_tomorrow_events()

    tomorrow_text, tomorrow_closing = build_tomorrow_section(
        tomorrow_events
    )

    money_text = build_money_section(finance)
    wedding_text = build_wedding_section(wedding)

    closing_text = build_closing_section(
        today,
        tomorrow_events,
    )

    return f"""🌙 <b>Evening Wrap</b>

Good evening, Shaun & Maria.

Another day done.

{DIVIDER}

📅 <b>Tomorrow</b>

{tomorrow_text}

{tomorrow_closing}

{DIVIDER}

💰 <b>Money</b>

{money_text}

{DIVIDER}

💍 <b>Wedding</b>

{wedding_text}

{DIVIDER}

🌙 <b>Good Night</b>

{closing_text}

Rest well ❤️

ShaunMariaOS will remember the rest.
"""