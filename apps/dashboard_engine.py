"""
ShaunMariaOS
Dashboard Engine
"""

from datetime import datetime

from apps.calendar_engine import get_today_events


def get_dashboard_message():
    today_events = get_today_events()
    now = datetime.now()

    event_count = len(today_events)

    next_event_text = "No upcoming events today"

    if today_events:
        next_event = today_events[0]
        title = next_event.get("summary", "Untitled Event")
        start = next_event["start"].get("dateTime", next_event["start"].get("date"))

        if "T" in start:
            time_part = start.split("T")[1][:5]
            next_event_text = f"{title} at {time_part}"
        else:
            next_event_text = f"{title} - All day"

    wedding_date = datetime(2026, 10, 31)
    wedding_days = (wedding_date - now).days

    message = f"""❤️ <b>ShaunMariaOS Dashboard</b>

📅 <b>Today</b>
{event_count} event(s)

🕒 <b>Next Event</b>
{next_event_text}

💍 <b>Wedding</b>
{wedding_days} days to go

🏠 <b>BTO</b>
Estimated TOP: Q3 2030

💰 <b>Finance</b>
Coming soon

👨‍💼 <b>Work</b>
Coming soon"""

    return message