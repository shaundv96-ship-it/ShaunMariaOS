"""
ShaunMariaOS

Dashboard Engine
"""

import logging
from typing import Any

from app_config import (
    APP_NAME,
    APP_STAGE,
    APP_VERSION,
    HOME_NAME,
    HOME_TOP,
)
from apps.advisor_engine import (
    get_advisor,
    get_next_action,
)
from apps.formatting_engine import money
from apps.greeting_engine import get_greeting
from apps.money_engine import get_money_summary
from apps.summary_engine import get_system_summary
from utils.time import sg_now
from utils.ui import build_screen
from utils.widgets import info_widget, metric_widget


logger = logging.getLogger(__name__)

VERSION = f"v{APP_VERSION} {APP_STAGE}"


# ==========================================================
# Default fallback data
# ==========================================================

DEFAULT_FINANCE_SUMMARY = {
    "salary": 0.0,
    "savings": 0.0,
    "bills": 0.0,
    "insurance": 0.0,
    "commitments": 0.0,
    "available": 0.0,
    "health": "⚠️ Finance unavailable",
}

DEFAULT_WEDDING_SUMMARY = {
    "days_remaining": "-",
    "guest_total": "-",
    "seats_available": "-",
    "total_budget": 0.0,
    "paid": 0.0,
    "balance": 0.0,
    "current_savings": 0.0,
    "shortfall": 0.0,
    "paid_percentage": 0.0,
}

DEFAULT_CALENDAR_SUMMARY = {
    "event_count": 0,
    "next_event": "⚠️ Calendar unavailable",
}

DEFAULT_MONEY_SUMMARY = {
    "income": 0.0,
    "expenses": 0.0,
    "allocated": 0.0,
    "monthly_cash_flow": 0.0,
    "available_money": 0.0,
}


# =================================================