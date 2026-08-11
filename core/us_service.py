"""
ShaunMariaOS

Us Service
Shared-life milestones for Shaun & Maria.
"""

from dataclasses import dataclass

from core.shared_goals import (
    get_chapter_goals,
    get_goals_for_us_page,
    get_timeline_goals,
)

from utils.time import sg_now
from utils.sheet_parser import get_budget_summary

@dataclass
class NextChapterResult:
    """Structured next-chapter result for any client."""

    success: bool
    status: str
    message: str
    title: str
    subtitle: str
    icon: str
    days_remaining: int | None = None

@dataclass
class SharedGoal:
    icon: str
    label: str
    title: str
    subtitle: str


@dataclass
class TimelineItem:
    icon: str
    title: str
    subtitle: str

@dataclass
class WeddingFund:
    total_budget: float
    paid: float
    balance: float
    current_savings: float
    shortfall: float
    paid_percentage: float

@dataclass
class UsOverviewResult:
    success: bool
    status: str
    message: str
    goals: list[SharedGoal]
    timeline: list[TimelineItem]
    wedding_fund: WeddingFund | None = None




def get_next_chapter() -> NextChapterResult:
    """Return the current shared-life milestone."""

    today = sg_now().date()

    chapter_goals = get_chapter_goals()

    for goal in chapter_goals:

        if (
            goal.chapter_type == "countdown"
            and goal.target_date
            and today <= goal.target_date
        ):
            days_remaining = (
                goal.target_date
                - today
            ).days

            if days_remaining == 0:
                title = "Today's the day! ❤️"
            else:
                title = (
                    f"{days_remaining} days to go"
                )

            return NextChapterResult(
                success=True,
                status=goal.id,
                message=(
                    f"{goal.title} milestone loaded."
                ),
                title=title,
                subtitle=(
                    f"{goal.title} · "
                    f"{goal.subtitle}"
                ),
                icon=goal.icon,
                days_remaining=days_remaining,
            )

        if (
            goal.chapter_type == "event"
            and goal.end_date
            and today <= goal.end_date
        ):
            if (
                goal.start_date
                and today < goal.start_date
            ):
                days_remaining = (
                    goal.start_date
                    - today
                ).days

                title = (
                    f"{days_remaining} days to "
                    f"{goal.title}"
                )

            else:
                days_remaining = 0
                title = f"{goal.title} time ❤️"

            return NextChapterResult(
                success=True,
                status=goal.id,
                message=(
                    f"{goal.title} milestone loaded."
                ),
                title=title,
                subtitle=goal.subtitle,
                icon=goal.icon,
                days_remaining=days_remaining,
            )

        if goal.chapter_type == "future":
            return NextChapterResult(
                success=True,
                status=goal.id,
                message=(
                    f"{goal.title} milestone loaded."
                ),
                title="Building our future home",
                subtitle=(
                    f"{goal.title} · "
                    f"{goal.subtitle}"
                ),
                icon=goal.icon,
                days_remaining=None,
            )

    return NextChapterResult(
        success=True,
        status="future",
        message="Future milestone loaded.",
        title="Our next chapter",
        subtitle="More adventures ahead. ❤️",
        icon="✨",
        days_remaining=None,
    )

def get_us_overview() -> UsOverviewResult:
    """Return shared goals and major upcoming milestones."""

    goals = [
        SharedGoal(
            icon=goal.icon,
            label=goal.label,
            title=goal.title,
            subtitle=goal.subtitle,
        )
        for goal in get_goals_for_us_page()
    ]

    timeline = [
        TimelineItem(
            icon=goal.icon,
            title=(
                "Honeymoon"
                if goal.id == "honeymoon"
                else (
                    "Our Home"
                    if goal.id == "home"
                    else goal.title
                )
            ),
            subtitle=goal.subtitle,
        )
        for goal in get_timeline_goals()
    ]

    wedding_fund = None

    try:
        budget = get_budget_summary(
            force_refresh=True,
        )

        wedding_fund = WeddingFund(
            total_budget=float(
                budget.get(
                    "total_budget",
                    0.0,
                )
            ),
            paid=float(
                budget.get(
                    "paid",
                    0.0,
                )
            ),
            balance=float(
                budget.get(
                    "balance",
                    0.0,
                )
            ),
            current_savings=float(
                budget.get(
                    "current_savings",
                    0.0,
                )
            ),
            shortfall=float(
                budget.get(
                    "shortfall",
                    0.0,
                )
            ),
            paid_percentage=float(
                budget.get(
                    "paid_percentage",
                    0.0,
                )
            ),
        )

    except Exception:
        wedding_fund = None

    return UsOverviewResult(
        success=True,
        status="loaded",
        message="Shared life overview loaded.",
        goals=goals,
        timeline=timeline,
        wedding_fund=wedding_fund,
    )