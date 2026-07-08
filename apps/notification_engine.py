"""
ShaunMariaOS

Notification Engine
"""

from apps.finance_engine import get_finance_summary
from apps.wedding_engine import get_wedding_summary
from apps.calendar_engine import get_calendar_summary


def get_notifications():

    notifications = []

    # Finance
    ...

    # Wedding
    ...

    # Calendar
    ...

    return notifications


def get_notification_message():
    """
    Formats notifications for Telegram.
    """

    notifications = get_notifications()

    message = "🔔 <b>Notifications</b>\n\n"

    if not notifications:
        return message + "🎉 You're all caught up!"

    for item in notifications:
        message += f"• {item}\n"

    return message