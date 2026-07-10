"""
ShaunMariaOS

Dashboard Engine
"""

from app_config import (
    APP_NAME,
    APP_STAGE,
    APP_VERSION,
    HOME_NAME,
    HOME_TOP,
)
from apps.summary_engine import get_system_summary
from apps.insight_engine import build_insights
from apps.greeting_engine import get_greeting
from utils.time import sg_now
from utils.ui import build_screen
from utils.widgets import info_widget, metric_widget
from apps.formatting_engine import money

VERSION = f"v{APP_VERSION} {APP_STAGE}"



def safe_finance_summary():
    """Return finance data without allowing dashboard failure."""
    try:
        return get_finance_summary()
    except Exception:
        return {
            "salary": 0,
            "savings": 0,
            "bills": 0,
            "insurance": 0,
            "commitments": 0,
            "available": 0,
            "health": "⚠️ Finance unavailable",
        }


def safe_wedding_summary():
    """Return wedding data without allowing dashboard failure."""
    try:
        return get_wedding_summary()
    except Exception:
        return {
            "days_remaining": "-",
            "guest_total": "-",
            "seats_available": "-",
            "total_budget": 0,
            "paid": 0,
            "balance": 0,
            "current_savings": 0,
            "shortfall": 0,
            "paid_percentage": 0,
        }


def safe_calendar_summary():
    """Return calendar data without allowing dashboard failure."""
    try:
        return get_calendar_summary()
    except Exception:
        return {
            "event_count": 0,
            "next_event": "⚠️ Calendar unavailable",
        }


def safe_insights():
    """Return generated insights without allowing dashboard failure."""
    try:
        insights = build_insights()
    except Exception:
        return "⚠️ Insights temporarily unavailable."

    if not insights:
        return "Everything looks good today."

    return "\n".join(f"• {insight}" for insight in insights)


def get_dashboard_message():
    """Build the main ShaunMariaOS dashboard."""
    summary = get_system_summary()

    finance = summary["finance"]
    wedding = summary["wedding"]
    calendar = summary["calendar"]

    today = sg_now().strftime("%A, %d %B %Y")

    sections = [
        info_widget(
            "👋 Greeting",
            f"{get_greeting()}\n📅 {today}",
        ),
        metric_widget(
            "💍 Wedding",
            f"{wedding['days_remaining']} days remaining\n"
            f"Guests: {wedding['guest_total']}\n"
            f"Budget: {wedding['paid_percentage']:.1f}% paid\n"
            f"Balance: {money(wedding['balance'])}",
        ),
        metric_widget(
            "💰 Money",
            f"Income: {money(finance['salary'])}\n"
            f"Commitments: {money(finance['commitments'])}\n"
            f"Available: {money(finance['available'])}\n"
            f"Status: {finance['health']}",
        ),
        info_widget(
            "📅 Today",
            calendar["next_event"],
        ),
        info_widget(
            "🏠 Home",
            f"{HOME_NAME}\n"
            f"Status: Booked ✅\n"
            f"TOP: {HOME_TOP}",
        ),
        info_widget(
            "🧠 Quick Insights",
            safe_insights(),
        ),
    ]

    return build_screen(
        f"❤️ <b>{APP_NAME}</b>",
        sections,
        VERSION,
    )