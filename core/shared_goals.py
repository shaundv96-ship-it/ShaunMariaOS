"""
ShaunMariaOS

Shared Goals
Reusable shared-life goals and milestones for Shaun & Maria.
"""

from dataclasses import dataclass
from datetime import date


@dataclass
class SharedGoal:
    """One shared goal or milestone."""

    id: str
    title: str
    label: str
    icon: str
    subtitle: str

    start_date: date | None = None
    end_date: date | None = None
    target_date: date | None = None

    priority: int = 0

    show_in_goals: bool = True
    show_in_timeline: bool = True
@dataclass
class SharedGoal:
    """One shared goal or milestone."""

    id: str
    title: str
    label: str
    icon: str
    subtitle: str

    start_date: date | None = None
    end_date: date | None = None
    target_date: date | None = None

    priority: int = 0

    show_in_goals: bool = True
    show_in_timeline: bool = True
    show_as_chapter: bool = False

    chapter_type: str = "milestone"

SHARED_GOALS = [
    SharedGoal(
        id="wedding",
        title="Wedding",
        label="OUR WEDDING",
        icon="💍",
        subtitle="31 October 2026",
        target_date=date(
            2026,
            10,
            31,
        ),
        priority=100,
        show_in_goals=False,
        show_in_timeline=True,
        show_as_chapter=True,
        chapter_type="countdown",
    ),

    SharedGoal(
        id="honeymoon",
        title="Melbourne",
        label="NEXT ADVENTURE",
        icon="✈️",
        subtitle="2–8 November 2026",
        start_date=date(
            2026,
            11,
            2,
        ),
        end_date=date(
            2026,
            11,
            8,
        ),
        priority=90,
        show_in_goals=True,
        show_in_timeline=True,
        show_as_chapter=True,
        chapter_type="event",
    ),

    SharedGoal(
        id="bto_fund",
        title="BTO Fund",
        label="OUR FUTURE",
        icon="💰",
        subtitle="Building our home together.",
        priority=80,
        show_in_goals=True,
        show_in_timeline=False,
        show_as_chapter=False,
    ),

    SharedGoal(
        id="home",
        title="OakVille @ AMK",
        label="OUR HOME",
        icon="🏠",
        subtitle="Projected TOP · Q3 2030",
        target_date=date(
            2030,
            9,
            30,
        ),
        priority=70,
        show_in_goals=True,
        show_in_timeline=True,
        show_as_chapter=True,
        chapter_type="future",
    ),
]

def get_all_shared_goals() -> list[SharedGoal]:
    """Return all configured shared goals."""

    return sorted(
        SHARED_GOALS,
        key=lambda goal: goal.priority,
        reverse=True,
    )


def get_goals_for_us_page() -> list[SharedGoal]:
    """Return goals that should appear on the Us page."""

    return [
        goal
        for goal in get_all_shared_goals()
        if goal.show_in_goals
    ]


def get_timeline_goals() -> list[SharedGoal]:
    """Return goals that should appear in the timeline."""

    return [
        goal
        for goal in get_all_shared_goals()
        if goal.show_in_timeline
    ]

def get_chapter_goals() -> list[SharedGoal]:
    """Return milestones that can become the next chapter."""

    return [
        goal
        for goal in get_all_shared_goals()
        if goal.show_as_chapter
    ]