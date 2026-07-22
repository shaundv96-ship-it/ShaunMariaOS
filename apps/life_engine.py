"""
ShaunMariaOS

LifeOS
"""

from utils.time import sg_now

from apps.summary_engine import get_system_summary
from apps.advisor_engine import get_advisor
from apps.calendar_engine import get_tomorrow_events


def get_life_snapshot():
    """
    Return a complete snapshot of Shaun & Maria's life.

    This becomes the single source of truth used by:
    - Daily Brief
    - Evening Wrap
    - Weekly Review
    - Monthly Reflection
    """

    summary = get_system_summary()

    return {
        "generated_at": sg_now(),

        "finance": summary.get("finance", {}),

        "calendar": summary.get("calendar", {}),

        "wedding": summary.get("wedding", {}),

        "tasks": summary.get("tasks", {}),

        "advisor": get_advisor(),
    }

calendar = {
    "tomorrow_events": get_tomorrow_events()
}