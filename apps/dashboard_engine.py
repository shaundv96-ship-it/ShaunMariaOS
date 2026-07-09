"""
ShaunMariaOS

Dashboard Engine
"""

from app_config import APP_NAME, APP_VERSION, APP_STAGE, HOME_NAME, HOME_TOP
from apps.calendar_engine import get_calendar_summary
from apps.finance_engine import get_finance_summary
from apps.wedding_engine import get_wedding_summary
from utils.time import sg_now
from utils.ui import build_screen
from utils.widgets import info_widget, metric_widget


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
        return "☀️ Good Morning Shaun & Maria"
    if hour < 18:
        return "🌤 Good Afternoon Shaun & Maria"
    if hour < 22:
        return "🌆 Good Evening Shaun & Maria"

    return "🌙 Good Night Shaun & Maria"


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
paid = wedding.get("paid", 0)
total_budget = wedding.get("total_budget", 0)

paid_percentage = (paid / total_budget * 100) if total_budget else 0

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

    return "\n".join(f"• {insight}" for insight in insights) or "Everything looks good today."


def get_dashboard_message():
    finance = safe_finance_summary()
    wedding = safe_wedding_summary()
    calendar = safe_calendar_summary()

    today = sg_now().strftime("%A, %d %B %Y")

    sections = [
        info_widget("👋 Greeting", f"{get_greeting()}\n📅 {today}"),
        metric_widget(
            "💍 Wedding",
            f"{wedding['days_remaining']} days remaining\n"
            f"Guests: {wedding['guest_total']}\n"
            f"Budget: {paid_percentage:.1f}% paid",1f}% paid",
        ),
        metric_widget(
            "💰 Money",
            f"Salary: {money(finance['salary'])}\n"
            f"Available: {money(finance['available'])}\n"
            f"Status: {finance['health']}",
        ),
        info_widget("📅 Today", calendar["next_event"]),
        info_widget(
            "🏠 Home",
            f"{HOME_NAME}\nStatus: Booked ✅\nTOP: {HOME_TOP}",
        ),
        info_widget("🧠 Quick Insight", build_insights(finance, wedding, calendar)),
    ]

    return build_screen(
        f"❤️ <b>{APP_NAME}</b>",
        sections,
        f"{VERSION} • Choose an option below 👇",
    )