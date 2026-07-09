"""
ShaunMariaOS

Time Utilities
"""

from datetime import datetime
from zoneinfo import ZoneInfo

SINGAPORE_TZ = ZoneInfo("Asia/Singapore")


def sg_now():
    """Current Singapore datetime."""
    return datetime.now(SINGAPORE_TZ)


def sg_today():
    """Current Singapore date."""
    return sg_now().date()


def current_hour():
    """Current hour in Singapore."""
    return sg_now().hour


def today_string():
    """Formatted Singapore date."""
    return sg_now().strftime("%A, %d %B %Y")