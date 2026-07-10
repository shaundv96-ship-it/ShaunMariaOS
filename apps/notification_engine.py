"""
ShaunMariaOS

Notification Engine
"""

from apps.formatting_engine import money
from apps.summary_engine import get_system_summary


def get_notifications():
    """
    Return important items that may need attention.

    Notifications should be more urgent and actionable than
    general advisor messages.
    """
    try:
        summary = get_system_summary()
    except Exception:
        return ["⚠️ System data is temporarily unavailable."]

    finance = summary["finance"]
    wedding = summary["wedding"]
    calendar = summary["calendar"]

    notifications = []

    # Finance
    available = finance.get("available", 0)

    if available < 0:
        notifications.append(
            f"🔴 Monthly commitments exceed income by {money(abs(available))}."
        )
    elif available < 500:
        notifications.append(
            f"🟠 Only {money(available)} remains after monthly commitments."
        )

    # Wedding countdown
    days_remaining = wedding.get("days_remaining")

    if isinstance(days_remaining, int):
        if days_remaining == 100:
            notifications.append("💍 The wedding is exactly 100 days away.")
        elif days_remaining == 30:
            notifications.append("💍 Only 30 days remain until the wedding.")
        elif days_remaining == 14:
            notifications.append("💍 The wedding is two weeks away.")
        elif days_remaining == 7:
            notifications.append("💍 The wedding is one week away.")
        elif 0 < days_remaining <= 3:
            notifications.append(
                f"🚨 Only {days_remaining} days remain until the wedding."
            )

    # Wedding funding
    shortfall = wedding.get("shortfall", 0)

    if shortfall > 0:
        notifications.append(
            f"💰 Wedding funding shortfall: {money(shortfall)}."
        )

    # Guest capacity
    seats_available = wedding.get("seats_available", "-")

    try:
        seats = int(seats_available)

        if seats <= 0:
            notifications.append("👥 The wedding guest list is full.")
        elif seats <= 5:
            notifications.append(
                f"👥 Only {seats} wedding guest seats remain."
            )
    except (ValueError, TypeError):
        pass

    # Calendar
    event_count = calendar.get("event_count", 0)

    if event_count >= 5:
        notifications.append(
            f"📅 Busy day ahead with {event_count} calendar events."
        )

    return notifications


def get_notification_message():
    """Format active notifications for Telegram."""
    notifications = get_notifications()

    if not notifications:
        return """🔔 <b>Notifications</b>

🎉 You're all caught up!"""

    lines = [
        "🔔 <b>Notifications</b>",
        "",
    ]

    lines.extend(f"• {item}" for item in notifications)

    return "\n".join(lines)