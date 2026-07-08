"""
ShaunMariaOS

Menu Navigation
"""

from telegram.error import BadRequest

from apps.about_engine import get_about
from apps.bills_engine import get_bills_dashboard
from apps.calendar_engine import format_today_events_for_telegram
from apps.dashboard_engine import get_dashboard_message
from apps.finance_engine import get_finance_dashboard
from apps.health_engine import get_health
from apps.insurance_engine import get_insurance_dashboard
from apps.salary_engine import get_salary_dashboard
from apps.version_engine import get_version
from apps.wedding_engine import (
    get_guestlist_summary,
    get_wedding_budget,
    get_wedding_dashboard,
    get_wedding_timeline,
)
from apps.menu_keyboard import (
    get_main_menu_buttons,
    get_money_menu_buttons,
    get_system_menu_buttons,
    get_wedding_menu_buttons,
)


async def safe_edit(query, message, keyboard):
    try:
        await query.edit_message_text(
            message,
            parse_mode="HTML",
            reply_markup=keyboard,
        )
    except BadRequest as error:
        if "Message is not modified" in str(error):
            return
        raise


async def handle_menu_button(update, context):
    query = update.callback_query
    await query.answer()

    routes = {
        "menu_main": (
            "❤️ <b>ShaunMariaOS</b>\n\nChoose an option below 👇",
            get_main_menu_buttons,
        ),
        "menu_today": (
            format_today_events_for_telegram,
            get_main_menu_buttons,
        ),
        "menu_dashboard": (
            get_dashboard_message,
            get_main_menu_buttons,
        ),
        "menu_wedding": (
            get_wedding_dashboard,
            get_wedding_menu_buttons,
        ),
        "wedding_budget": (
            get_wedding_budget,
            get_wedding_menu_buttons,
        ),
        "wedding_guestlist": (
            get_guestlist_summary,
            get_wedding_menu_buttons,
        ),
        "wedding_timeline": (
            get_wedding_timeline,
            get_wedding_menu_buttons,
        ),
        "menu_money": (
            get_finance_dashboard,
            get_money_menu_buttons,
        ),
        "money_salary": (
            get_salary_dashboard,
            get_money_menu_buttons,
        ),
        "money_bills": (
            get_bills_dashboard,
            get_money_menu_buttons,
        ),
        "money_insurance": (
            get_insurance_dashboard,
            get_money_menu_buttons,
        ),
        "menu_system": (
            get_health,
            get_system_menu_buttons,
        ),
        "system_version": (
            get_version,
            get_system_menu_buttons,
        ),
        "system_about": (
            get_about,
            get_system_menu_buttons,
        ),
    }

    page = routes.get(query.data)

    if not page:
        await safe_edit(
            query,
            "⚠️ Unknown option.",
            get_main_menu_buttons(),
        )
        return

    message_source, keyboard_source = page

    if callable(message_source):
        message = message_source()
    else:
        message = message_source

    keyboard = keyboard_source()

    await safe_edit(query, message, keyboard)