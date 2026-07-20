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
from apps.advisor_engine import get_advisor
from apps.formatting_engine import money
from apps.greeting_engine import get_greeting
from apps.summary_engine import get_system_summary
from apps.money_engine import get_money_summary
from utils.time import sg_now
from utils.ui import build_screen
from utils.widgets import info_widget, metric_widget


VERSION = f"v{APP_VERSION} {APP_STAGE}"


def safe_system_summary():
    """Return system data without allowing the dashboard to fail."""
    try:
        return get_system_summary()
    except Exception:
        return {
            "finance": {
                "salary": 0,
                "savings": 0,
                "bills": 0,
                "insurance": 0,
                "commitments": 0,
                "available": 0,
                "health": "⚠️ Finance unavailable",
            },
            "wedding": {
                "days_remaining": "-",
                "guest_total": "-",
                "seats_available": "-",
                "total_budget": 0,
                "paid": 0,
                "balance": 0,
                "current_savings": 0,
                "shortfall": 0,
                "paid_percentage": 0,
            },
            "calendar": {
                "event_count": 0,
                "next_event": "⚠️ Calendar unavailable",
            },
        }

def safe_money_summary() -> dict:
    """Return MoneyOS data without allowing the dashboard to fail."""
    try:
        return get_money_summary()
    except Exception:
        return {
            "income": 0.0,
            "expenses": 0.0,
            "allocated": 0.0,
            "monthly_cash_flow": 0.0,
            "available_money": 0.0,
        }

def safe_advice():
    """Return advisor messages without allowing the dashboard to fail."""
    try:
        advice = get_advisor()
    except Exception:
        return "⚠️ Advice temporarily unavailable."

    if not advice:
        return "Everything looks good today."

    return "\n".join(f"• {item}" for item in advice)


def get_dashboard_message():
    """Build the main ShaunMariaOS dashboard."""
    summary = safe_system_summary()
    money_summary = safe_money_summary()

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
            f"Income received: {money(money_summary['income'])}\n"
            f"Spent: {money(money_summary['expenses'])}\n"
            f"Allocated: {money(money_summary['allocated'])}\n"
            f"Available to spend: "
            f"{money(money_summary['available_money'])}",
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
            "🧠 Advisor",
            safe_advice(),
        ),
    ]

    return build_screen(
        f"❤️ <b>{APP_NAME}</b>",
        sections,
        VERSION,
    )
    
