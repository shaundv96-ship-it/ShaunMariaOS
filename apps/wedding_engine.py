"""
ShaunMariaOS

Wedding Engine
"""

from datetime import datetime

from apps.database_engine import (
    get_budget_sheet,
    get_guestlist_sheet,
    get_timeline_sheet,
)
from utils.time import sg_now

WEDDING_DATE = datetime(2026, 10, 31)


def money(value):
    try:
        amount = float(str(value).replace("$", "").replace(",", "").strip())
        return f"${amount:,.2f}"
    except (ValueError, TypeError):
        return str(value)


def number(value):
    try:
        return float(str(value).replace("$", "").replace(",", "").strip())
    except (ValueError, TypeError):
        return 0


def wedding_days_remaining():
    today = sg_now().date()
    return (WEDDING_DATE.date() - today).days


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


def extract_budget_values(rows):
    print("\n========== WEDDING BUDGET ==========")
    for row in rows:
        print(row)
    print("====================================\n")

    total_budget = 0
    paid = 0
    balance = 0
    current_savings = 0

    for row in rows:
        row_text = " ".join(str(cell) for cell in row)

        if len(row) >= 4 and (
            "Total Budget" in row_text
            or "45,444" in row_text
            or "45444" in row_text
        ):
            total_budget = number(row[1])
            paid = number(row[2])
            balance = number(row[3])

        if "Current Savings" in row_text and len(row) > 1:
            current_savings = number(row[1])

    shortfall = balance - current_savings
    paid_percentage = (paid / total_budget * 100) if total_budget else 0

    return {
        "total_budget": total_budget,
        "paid": paid,
        "balance": balance,
        "current_savings": current_savings,
        "shortfall": shortfall,
        "paid_percentage": paid_percentage,
    }

def extract_guestlist_values(rows):
    shaun_total = "-"
    maria_total = "-"
    total_guests = "-"
    seats_available = "-"
    cards_total = "-"
    cards_shaun = "-"
    cards_maria = "-"
    cards_balance = "-"

    total_counter = 0

    for row in rows:
        for i, cell in enumerate(row):
            value = str(cell).strip()

            if value == "Total:" and i + 1 < len(row):
                total_counter += 1

                if total_counter == 1:
                    shaun_total = row[i + 1]
                elif total_counter == 2:
                    maria_total = row[i + 1]

            if "Total as of" in value and i + 1 < len(row):
                total_guests = row[i + 1]

            if value == "seats available" and i + 1 < len(row):
                seats_available = row[i + 1]

            if value == "Cards:" and i + 1 < len(row):
                cards_total = row[i + 1]

            if value == "Shaun:" and i + 1 < len(row):
                cards_shaun = row[i + 1]

            if value == "Maria:" and i + 1 < len(row):
                cards_maria = row[i + 1]

            if value == "Balance:" and i + 1 < len(row):
                cards_balance = row[i + 1]

    return {
        "shaun_total": shaun_total,
        "maria_total": maria_total,
        "total_guests": total_guests,
        "seats_available": seats_available,
        "cards_total": cards_total,
        "cards_shaun": cards_shaun,
        "cards_maria": cards_maria,
        "cards_balance": cards_balance,
    }


def get_wedding_dashboard():
    days_remaining = wedding_days_remaining()

    return f"""💍 <b>Shaun & Maria Wedding</b>

📅 <b>Wedding Date</b>
31 October 2026

⏳ <b>Countdown</b>
{days_remaining} days to go

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
        "days_remaining": wedding_days_remaining(),
        "total_budget": budget["total_budget"],
        "paid": budget["paid"],
        "balance": budget["balance"],
        "current_savings": budget["current_savings"],
        "shortfall": budget["shortfall"],
        "paid_percentage": budget["paid_percentage"],
        "guest_total": guestlist["total_guests"],
        "seats_available": guestlist["seats_available"],
    }


def get_wedding_timeline():
    rows = get_timeline_sheet()
    now = sg_now()

    events = []

    for row in rows:
        padded = row + [""] * 7

        dday_time = padded[0]
        dday_activity = padded[1]
        dday_poc = padded[2]

        reception_time = padded[4]
        reception_activity = padded[5]
        reception_poc = padded[6]

        if parse_time_to_datetime(dday_time) and dday_activity:
            events.append({
                "time": dday_time,
                "activity": dday_activity,
                "poc": dday_poc,
                "section": "D-Day",
            })

        if parse_time_to_datetime(reception_time) and reception_activity:
            events.append({
                "time": reception_time,
                "activity": reception_activity,
                "poc": reception_poc,
                "section": "Reception",
            })

    if not events:
        return "⚠️ No timeline items found."

    events.sort(key=lambda event: parse_time_to_datetime(event["time"]))

    days_remaining = wedding_days_remaining()

    message = "❤️ <b>Wedding Operations Timeline</b>\n\n"

    if days_remaining > 0:
        message += f"⏳ <b>Wedding Countdown</b>\n{days_remaining} days to go\n\n"
        first = events[0]
        message += "⏭️ <b>First Task</b>\n"
        message += f"{first['time']} - {first['activity']}\n"
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

            if event_dt and event_dt > now:
                next_event = event
                break

        if current_event:
            message += "📍 <b>Current / Latest Task</b>\n"
            message += f"{current_event['time']} - {current_event['activity']}\n"
            if current_event["poc"]:
                message += f"POC: {current_event['poc']}\n"
            message += "\n"

        if next_event:
            message += "⏭️ <b>Next Task</b>\n"
            message += f"{next_event['time']} - {next_event['activity']}\n"
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