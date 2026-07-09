"""
ShaunMariaOS

Wedding Engine
"""

from datetime import datetime

from apps.database_engine import get_budget_sheet, get_guestlist_sheet, get_timeline_sheet
from utils.time import sg_now

WEDDING_DATE = datetime(2026, 10, 31)


def number(value):
    try:
        return float(str(value).replace("$", "").replace(",", "").strip())
    except (ValueError, TypeError):
        return 0


def money(value):
    amount = number(value)
    return f"${amount:,.2f}"


def wedding_days_remaining():
    return (WEDDING_DATE.date() - sg_now().date()).days


def parse_time_to_datetime(time_text):
    text = str(time_text).strip().lower()

    if not text:
        return None

    for fmt in ["%I.%M%p", "%I:%M%p", "%I.%M %p", "%I:%M %p", "%H:%M"]:
        try:
            parsed_time = datetime.strptime(text, fmt).time()
            return datetime.combine(WEDDING_DATE.date(), parsed_time)
        except ValueError:
            continue

    return None


def extract_budget_values(rows):
    budget = {
        "total_budget": 0,
        "paid": 0,
        "balance": 0,
        "current_savings": 0,
    }

    for row in rows:
        row_text = " ".join(str(cell) for cell in row)

        is_total_row = (
            len(row) >= 4
            and str(row[0]).strip() == ""
            and str(row[1]).strip().startswith("$")
            and str(row[2]).strip().startswith("$")
            and str(row[3]).strip().startswith("$")
        )

        if is_total_row:
            budget["total_budget"] = number(row[1])
            budget["paid"] = number(row[2])
            budget["balance"] = number(row[3])

        if "Current Savings" in row_text and len(row) > 1:
            budget["current_savings"] = number(row[1])

    budget["shortfall"] = budget["balance"] - budget["current_savings"]
    budget["paid_percentage"] = (
        budget["paid"] / budget["total_budget"] * 100
        if budget["total_budget"]
        else 0
    )

    return budget


def extract_guestlist_values(rows):
    guestlist = {
        "shaun_total": "-",
        "maria_total": "-",
        "total_guests": "-",
        "seats_available": "-",
        "cards_total": "-",
        "cards_shaun": "-",
        "cards_maria": "-",
        "cards_balance": "-",
    }

    total_counter = 0

    for row in rows:
        for index, cell in enumerate(row):
            value = str(cell).strip()
            next_value = row[index + 1] if index + 1 < len(row) else "-"

            if value == "Total:":
                total_counter += 1
                if total_counter == 1:
                    guestlist["shaun_total"] = next_value
                elif total_counter == 2:
                    guestlist["maria_total"] = next_value

            elif "Total as of" in value:
                guestlist["total_guests"] = next_value

            elif value == "seats available":
                guestlist["seats_available"] = next_value

            elif value == "Cards:":
                guestlist["cards_total"] = next_value

            elif value == "Shaun:":
                guestlist["cards_shaun"] = next_value

            elif value == "Maria:":
                guestlist["cards_maria"] = next_value

            elif value == "Balance:":
                guestlist["cards_balance"] = next_value

    return guestlist


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
    budget = extract_budget_values(get_budget_sheet())

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
    guestlist = extract_guestlist_values(get_guestlist_sheet())

    return f"""👥 <b>Guestlist Summary</b>

👔 <b>Shaun</b>
{guestlist["shaun_total"]}

👰 <b>Maria</b>
{guestlist["maria_total"]}

👥 <b>Total Guests</b>
{guestlist["total_guests"]}

🪑 <b>Seats Available</b>
{guestlist["seats_available"]}

💌 <b>Physical Cards</b>
Total: {guestlist["cards_total"]}
Shaun: {guestlist["cards_shaun"]}
Maria: {guestlist["cards_maria"]}
Balance: {guestlist["cards_balance"]}

📊 <b>Source</b>
Live from Google Sheets"""


def get_wedding_summary():
    budget = extract_budget_values(get_budget_sheet())
    guestlist = extract_guestlist_values(get_guestlist_sheet())

    return {
        **budget,
        "days_remaining": wedding_days_remaining(),
        "guest_total": guestlist["total_guests"],
        "seats_available": guestlist["seats_available"],
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
            if parse_time_to_datetime(time_text) and activity:
                events.append(
                    {
                        "time": time_text,
                        "activity": activity,
                        "poc": poc,
                        "section": section,
                    }
                )

    return sorted(events, key=lambda event: parse_time_to_datetime(event["time"]))


def get_wedding_timeline():
    events = build_timeline_events(get_timeline_sheet())
    now = sg_now()
    days_remaining = wedding_days_remaining()

    if not events:
        return "⚠️ No timeline items found."

    message = "❤️ <b>Wedding Operations Timeline</b>\n\n"

    if days_remaining > 0:
        first = events[0]
        message += f"⏳ <b>Wedding Countdown</b>\n{days_remaining} days to go\n\n"
        message += f"⏭️ <b>First Task</b>\n{first['time']} - {first['activity']}\n"
        if first["poc"]:
            message += f"POC: {first['poc']}\n"
        message += "\n"

    elif days_remaining == 0:
        message += "🟢 <b>Wedding Day Live Mode</b>\n\n"

        current_event = None
        next_event = None

        for event in events:
            event_dt = parse_time_to_datetime(event["time"])
            if event_dt and event_dt <= now:
                current_event = event
            elif event_dt and event_dt > now:
                next_event = event
                break

        if current_event:
            message += f"📍 <b>Current / Latest Task</b>\n{current_event['time']} - {current_event['activity']}\n"
            if current_event["poc"]:
                message += f"POC: {current_event['poc']}\n"
            message += "\n"

        if next_event:
            message += f"⏭️ <b>Next Task</b>\n{next_event['time']} - {next_event['activity']}\n"
            if next_event["poc"]:
                message += f"POC: {next_event['poc']}\n"
            message += "\n"

    else:
        message += "📦 <b>Wedding timeline archived.</b>\n\n"

    message += "📋 <b>Full Timeline</b>\n"

    for event in events:
        poc_text = f" — {event['poc']}" if event["poc"] else ""
        message += f"\n{event['time']} - {event['activity']}{poc_text}"

    message += "\n\n📊 <b>Source</b>\nLive from Google Sheets"

    return message