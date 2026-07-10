"""
ShaunMariaOS

Summary Engine
"""

from apps.calendar_engine import get_calendar_summary
from apps.finance_engine import get_finance_summary
from apps.wedding_engine import get_wedding_summary


def get_system_summary():
    return {
        "finance": get_finance_summary(),
        "wedding": get_wedding_summary(),
        "calendar": get_calendar_summary(),
    }