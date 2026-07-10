"""
ShaunMariaOS

Wedding Engine
"""

from datetime import datetime

from apps.database_engine import get_timeline_sheet
from utils.sheet_parser import get_budget_summary, get_guest_summary
from utils.time import sg_now
from apps.formatting_engine import money

WEDDING_DATE = datetime(2026, 10, 31)


def wedding_days_remaining():
    return (WEDDING_DATE.date() - sg_now().date()).days


def parse_time_to_datetime(time_text):
    text = str(time_text).strip().lower()

    if not text:
        return None

    formats = [
        "%I.%M%p",
        "%I:%M%p",
        "%I.%M %p",
        "%I:%M %p",
        "%H:%M",
    ]

    for fmt in formats:
        try:
            parsed_time = datetime.strptime(text, fmt).time()
            return datetime.combine(WEDDING_DATE.date(), parsed_time)
        except ValueError:
            continue

    return None


def get_wedding_dashboard():
    return f"""💍 <b>Shaun & Maria Wedding</b>

📅 <b>Wedding Date</b>
31 October 2026

⏳ <b>Countdown</b>
{wedding_days_remaining()} days to go

Commands:
/weddingbudget - Budget summary
/guestlist - Guestlist summary
/timeline - Wedding day timeline"""


def get_wedding_budget():
    budget = get_budget_summary()

    return f"""💰 <b>Wedding Budget</b>

💍 <b>Total Budget</b>
{money(budget["total_budget"])}

✅ <b>Paid</b>
{money(budget["paid"])}

📉 <b>Balance</b>
{money(budget["balance"])}

🏦 <b>Current Savings</b>
{money(budget["current_savings"])}

⚠️ <b>Shortfall</b>
{money(budget["shortfall"])}

📊 <b>Source</b>
Live from Google Sheets"""


def get_guestlist_summary():
    guest = get_guest_summary()

    return f"""👥 <b>Guestlist Summary</b>

👔 <b>Shaun</b>
{guest["shaun_total"]}

👰 <b>Maria</b>
{guest["maria_total"]}

👥 <b>Total Guests</b>
{guest["total_guests"]}

🪑 <b>Seats Available</b>
{guest["seats_available"]}

💌 <b>Physical Cards</b>
Total: {guest["cards_total"]}
Shaun: {guest["cards_shaun"]}
Maria: {guest["cards_maria"]}
Balance: {guest["cards_balance"]}

📊 <b>Source</b>
Live from Google Sheets"""


def get_wedding_summary():
    budget = get_budget_summary()
    guest = get_guest_summary()

    return {
        **budget,
        "days_remaining": wedding_days_remaining(),
        "guest_total": guest["total_guests"],
        "seats_available": guest["seats_available"],
    }


def build_timeline_events(rows):
    events = []

    for row in rows:
        padded = row + [""] * 7

        timeline_items = [
            (padded[0], padded[1], padded[2], "D-Day"),
            (padded[4], padded[5], padded[6], "Reception"),
        ]

        for time_text, activity, poc, section in timeline_items:
            event_time = parse_time_to_datetime(time_text)

            if event_time and activity:
                events.append(
                    {
                        "time": time_text,
                        "datetime": event_time,
                        "activity": activity,
                        "poc": poc,
                        "section": section,
                    }
                )

    return sorted(events, key=lambda event: event["datetime"])


def format_timeline_event(event):
    message = f"{event['time']} - {event['activity']}"

    if event["poc"]:
        message += f"\nPOC: {event['poc']}"

    return message


def get_wedding_timeline():
    events = build_timeline_events(get_timeline_sheet())

    if not events:
        return "⚠️ No timeline items found."

    now = sg_now()
    days_remaining = wedding_days_remaining()

    lines = ["❤️ <b>Wedding Operations Timeline</b>", ""]

    if days_remaining > 0:
        lines.extend(
            [
                "⏳ <b>Wedding Countdown</b>",
                f"{days_remaining} days to go",
                "",
                "⏭️ <b>First Task</b>",
                format_timeline_event(events[0]),
                "",
            ]
        )

    elif days_remaining == 0:
        lines.extend(
            [
                "🟢 <b>Wedding Day Live Mode</b>",
                "",
            ]
        )

        current_event = None
        next_event = None

        for event in events:
            event_datetime = event["datetime"]

            if event_datetime <= now:
                current_event = event
            elif event_datetime > now:
                next_event = event
                break

        if current_event:
            lines.extend(
                [
                    "📍 <b>Current / Latest Task</b>",
                    format_timeline_event(current_event),
                    "",
                ]
            )

        if next_event:
            lines.extend(
                [
                    "⏭️ <b>Next Task</b>",
                    format_timeline_event(next_event),
                    "",
                ]
            )

    else:
        lines.extend(
            [
                "📦 <b>Wedding timeline archived.</b>",
                "",
            ]
        )

    lines.append("📋 <b>Full Timeline</b>")

    for event in events:
        poc_text = f" — {event['poc']}" if event["poc"] else ""
        lines.append(f"{event['time']} - {event['activity']}{poc_text}")

    lines.extend(
        [
            "",
            "📊 <b>Source</b>",
            "Live from Google Sheets",
        ]
    )

    return "\n".join(lines)