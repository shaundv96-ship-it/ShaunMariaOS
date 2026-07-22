"""
ShaunMariaOS

Weekly Review Engine
"""

from html import escape

from apps.formatting_engine import money
from apps.life_engine import get_life_snapshot
from apps.task_engine import get_open_tasks


DIVIDER = "━━━━━━━━━━━━━━━━━━"


def build_money_section(finance):
    """Summarise the current month's finances."""

    income = finance.get("income", 0)
    expenses = finance.get("expenses", 0)
    available = finance.get("available", 0)

    lines = [
        f"• Income recorded: {money(income)}",
        f"• Spending this month: {money(expenses)}",
        f"• Available balance: {money(available)}",
    ]

    if income <= 0 and expenses > 0:
        lines.append(
            "\nYour salary has not been recorded yet."
        )
    elif available < 0:
        lines.append(
            "\nYour recorded spending currently exceeds your income."
        )
    else:
        lines.append(
            "\nMoneyOS is up to date."
        )

    return "\n".join(lines)


def build_wedding_section(wedding):
    """Summarise the wedding countdown and funding."""

    days_remaining = wedding.get("days_remaining", 0)
    paid_percentage = wedding.get("paid_percentage", 0)

    if days_remaining < 0:
        return "The wedding chapter is complete ❤️"

    if days_remaining == 0:
        return "Today is the wedding day ❤️"

    return (
        f"• {days_remaining} days remaining\n"
        f"• {paid_percentage:.0f}% funded\n\n"
        "Another week closer to 31 October ❤️"
    )


def build_task_section(tasks):
    """Summarise currently open tasks."""

    if not tasks:
        return (
            "No open tasks.\n\n"
            "You’re starting the new week with a clear list."
        )

    lines = [
        f"You have {len(tasks)} open task"
        f"{'s' if len(tasks) != 1 else ''}:"
    ]

    for task in tasks[:5]:
        task_id = task.get("id", "?")
        task_text = escape(
            str(task.get("task", "Untitled task"))
        )
        owner = escape(
            str(task.get("owner", "Unassigned"))
        )

        lines.append(
            f"\n• <b>{task_id}. {task_text}</b>"
            f"\n  👤 {owner}"
        )

    if len(tasks) > 5:
        remaining = len(tasks) - 5
        lines.append(
            f"\n• Plus {remaining} more task"
            f"{'s' if remaining != 1 else ''}"
        )

    return "\n".join(lines)


def build_weekly_reflection(finance, wedding, tasks):
    """Return one simple reflection for the week ahead."""

    income = finance.get("income", 0)
    expenses = finance.get("expenses", 0)
    available = finance.get("available", 0)
    days_remaining = wedding.get("days_remaining", 0)

    if len(tasks) >= 5:
        return (
            "There are several open tasks carrying into the new week.\n\n"
            "Choose the three that would make the biggest difference."
        )

    if income <= 0 and expenses > 0:
        return (
            "MoneyOS is still waiting for this month’s salary entry.\n\n"
            "Recording it will give you a clearer view of the month."
        )

    if available < 0:
        return (
            "This week may be a good time to review your spending "
            "and upcoming commitments."
        )

    if 0 < days_remaining <= 100:
        return (
            "The wedding is getting closer.\n\n"
            "Keep focusing on one manageable decision at a time."
        )

    if not tasks:
        return (
            "You’re entering the new week with no open tasks.\n\n"
            "Enjoy the clean start."
        )

    return (
        "The foundations are in place for the week ahead.\n\n"
        "Focus on steady progress rather than doing everything at once."
    )


def get_weekly_review():
    """Build the Sunday Weekly Review."""

    life = get_life_snapshot()

    finance = life["finance"]
    wedding = life["wedding"]
    tasks = get_open_tasks()

    money_text = build_money_section(finance)
    wedding_text = build_wedding_section(wedding)
    task_text = build_task_section(tasks)

    reflection_text = build_weekly_reflection(
        finance,
        wedding,
        tasks,
    )

    return f"""📖 <b>Weekly Review</b>

Good evening, Shaun & Maria.

Here’s where life currently stands as a new week begins.

{DIVIDER}

💰 <b>Money</b>

{money_text}

{DIVIDER}

💍 <b>Wedding</b>

{wedding_text}

{DIVIDER}

✅ <b>Open Tasks</b>

{task_text}

{DIVIDER}

✨ <b>Weekly Reflection</b>

{reflection_text}

Have a good week ahead ❤️

ShaunMariaOS will remember the rest.
"""