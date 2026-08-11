"""
ShaunMariaOS

Advisor Service
Creates a simple shared-life status from live OS data.
"""

from dataclasses import dataclass

from core.money_service import get_money_overview
from core.task_service import get_tasks
from core.us_service import get_next_chapter


@dataclass
class AdvisorResult:
    """Structured ShaunMaria Advisor result."""

    success: bool
    status: str
    title: str
    message: str


def get_advisor() -> AdvisorResult:
    """Build the current ShaunMariaOS Home advisor."""

    money = get_money_overview()
    tasks = get_tasks()
    chapter = get_next_chapter()

    if not money.success:
        return AdvisorResult(
            success=False,
            status="money_unavailable",
            title="MoneyOS needs attention.",
            message=(
                "I couldn't load your current "
                "money position."
            ),
        )

    available = money.available_money
    task_count = (
        len(tasks.tasks)
        if tasks.success
        else 0
    )

    days_remaining = (
        chapter.days_remaining
        if chapter.success
        else None
    )

    #
    # Main financial status
    #

    if available < 0:
        title = "Money is a little tight."

        message = (
            f"You're currently "
            f"${abs(available):,.2f} over "
            f"your available spending amount."
        )

    elif available < 500:
        title = "Keep an eye on spending."

        message = (
            f"You have ${available:,.2f} "
            f"available to spend."
        )

    else:
        title = "Things are looking steady."

        message = (
            f"You have ${available:,.2f} "
            f"available to spend."
        )

    #
    # Add task context
    #

    if task_count == 1:
        message += (
            " You have 1 task remaining."
        )

    elif task_count > 1:
        message += (
            f" You have {task_count} "
            f"tasks remaining."
        )

    elif tasks.success:
        message += (
            " You're all caught up on tasks."
        )

    #
    # Add next-chapter context
    #

    if (
        days_remaining is not None
        and days_remaining > 0
    ):
        message += (
            f" Your next chapter is "
            f"{days_remaining} days away."
        )

    elif (
        chapter.success
        and chapter.status == "wedding"
        and days_remaining == 0
    ):
        message += (
            " Today's the big day. ❤️"
        )

    return AdvisorResult(
        success=True,
        status="loaded",
        title=title,
        message=message,
    )