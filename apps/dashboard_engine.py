"""
ShaunMariaOS

Dashboard Engine
"""

from app_config import APP_NAME, APP_VERSION, APP_STAGE, HOME_NAME, HOME_TOP
from apps.calendar_engine import get_calendar_summary
from apps.finance_engine import get_finance_summary
from apps.wedding_engine import get_wedding_summary
from utils.time import sg_now

VERSION = f"v{APP_VERSION} {APP_STAGE}"


def money(value):
    try:
        amount = float(value)
        return f"${amount:,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


def get_greeting():
    hour = sg_now().hour

    if hour < 12:
        return "☀️ Good Morning Shaun"
    if hour < 18:
        return "🌤 Good Afternoon Shaun"
    if hour < 22:
        return "🌆 Good Evening Shaun"

    return "🌙 Good Night Shaun"


def safe_finance_summary():
    try:
        return get_finance_summary()
    except Exception:
        return {
            "salary": 0,
            "available": 0,
            "health": "⚠️ Finance unavailable",
        }


def safe_wedding_summary():
    try:
        return get_wedding_summary()
    except Exception:
        return {
            "days_remaining": "-",
            "guest_total": "-",
            "seats_available": "-",
            "paid": 0,
            "total_budget": 0,
            "paid_percentage": 0,
        }


def safe_calendar_summary():
    try:
        return get_calendar_summary()
    except Exception:
        return {
            "event_count": 0,
            "next_event": "Calendar unavailable",
        }


def build_insights(finance, wedding, calendar):
    insights = []

    if finance["available"] >= 1000:
        insights.append("💰 Cash flow is healthy.")
    elif finance["available"] > 0:
        insights.append("💰 Cash flow is manageable.")
    else:
        insights.append("⚠️ Review monthly cash flow.")

    if wedding["seats_available"] != "-":
        insights.append(f"💒 {wedding['seats_available']} wedding seats remaining.")

    if wedding["paid_percentage"] >= 40:
        insights.append("✅ Wedding budget is progressing well.")

    if calendar["event_count"] == 0:
        insights.append("📅 No calendar events today.")

    if not insights:
        insights.append("Everything looks good today.")

    return insights


def get_dashboard_message():
    finance = safe_finance_summary()
    wedding = safe_wedding_summary()
    calendar = safe_calendar_summary()

    today = sg_now().strftime("%A, %d %B %Y")
    insights = build_insights(finance, wedding, calendar)

    message = f"""❤️ <b>{APP_NAME}</b>
{VERSION}

{get_greeting()}

📅 {today}

━━━━━━━━━━━━━━━━━━

💒 <b>Wedding</b>

⏳ {wedding['days_remaining']} days remaining

👥 Guests
{wedding['guest_total']}

💰 Budget
{wedding['paid_percentage']:.1f}% Paid
{money(wedding.get('paid', 0))} / {money(wedding.get('total_budget', 0))}

━━━━━━━━━━━━━━━━━━

💵 <b>Finance</b>

💰 Salary
{money(finance['salary'])}

💳 Available Cash
{money(finance['available'])}

📊 Cash Flow
{finance['health']}

━━━━━━━━━━━━━━━━━━

📅 <b>Today</b>

{calendar['next_event']}

━━━━━━━━━━━━━━━━━━

🏠 <b>Home</b>

{HOME_NAME}

Status
Booked ✅

TOP
{HOME_TOP}

━━━━━━━━━━━━━━━━━━

🧠 <b>Quick Insight</b>
"""

    for insight in insights:
        message += f"\n• {insight}"

    message += f"""

━━━━━━━━━━━━━━━━━━

❤️ {VERSION}
"""

    return message