"""
ShaunMariaOS

Menu Navigation
"""

from apps.calendar_engine import format_today_events_for_telegram
from apps.dashboard_engine import get_dashboard_message
from apps.finance_engine import get_finance_dashboard
from apps.wedding_engine import (
    get_wedding_dashboard,
    get_wedding_budget,
    get_guestlist_summary,
    get_wedding_timeline,
)
from apps.bills_engine import get_bills_dashboard
from apps.salary_engine import get_salary_dashboard
from apps.insurance_engine import get_insurance_dashboard
from apps.health_engine import get_health
from apps.version_engine import get_version
from apps.about_engine import get_about
from apps.menu_keyboard import (
    get_main_menu_buttons,
    get_wedding_menu_buttons,
    get_money_menu_buttons,
    get_system_menu_buttons,
)


async def handle_menu_button(update, context):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "menu_main":
        await query.edit_message_text(
            "❤️ <b>ShaunMariaOS</b>\n\nChoose an option below 👇",
            parse_mode="HTML",
            reply_markup=get_main_menu_buttons(),
        )

    elif data == "menu_today":
        await query.edit_message_text(
            format_today_events_for_telegram(),
            parse_mode="HTML",
            reply_markup=get_main_menu_buttons(),
        )

    elif data == "menu_dashboard":
        await query.edit_message_text(
            get_dashboard_message(),
            parse_mode="HTML",
            reply_markup=get_main_menu_buttons(),
        )

    elif data == "menu_wedding":
        await query.edit_message_text(
            get_wedding_dashboard(),
            parse_mode="HTML",
            reply_markup=get_wedding_menu_buttons(),
        )

    elif data == "wedding_budget":
        await query.edit_message_text(
            get_wedding_budget(),
            parse_mode="HTML",
            reply_markup=get_wedding_menu_buttons(),
        )

    elif data == "wedding_guestlist":
        await query.edit_message_text(
            get_guestlist_summary(),
            parse_mode="HTML",
            reply_markup=get_wedding_menu_buttons(),
        )

    elif data == "wedding_timeline":
        await query.edit_message_text(
            get_wedding_timeline(),
            parse_mode="HTML",
            reply_markup=get_wedding_menu_buttons(),
        )

    elif data == "menu_money":
        await query.edit_message_text(
            get_finance_dashboard(),
            parse_mode="HTML",
            reply_markup=get_money_menu_buttons(),
        )

    elif data == "money_salary":
        await query.edit_message_text(
            get_salary_dashboard(),
            parse_mode="HTML",
            reply_markup=get_money_menu_buttons(),
        )

    elif data == "money_bills":
        await query.edit_message_text(
            get_bills_dashboard(),
            parse_mode="HTML",
            reply_markup=get_money_menu_buttons(),
        )

    elif data == "money_insurance":
        await query.edit_message_text(
            get_insurance_dashboard(),
            parse_mode="HTML",
            reply_markup=get_money_menu_buttons(),
        )

    elif data == "menu_system":
        await query.edit_message_text(
            get_health(),
            parse_mode="HTML",
            reply_markup=get_system_menu_buttons(),
        )

    elif data == "system_version":
        await query.edit_message_text(
            get_version(),
            parse_mode="HTML",
            reply_markup=get_system_menu_buttons(),
        )

    elif data == "system_about":
        await query.edit_message_text(
            get_about(),
            parse_mode="HTML",
            reply_markup=get_system_menu_buttons(),
        )

    else:
        await query.edit_message_text(
            "⚠️ Unknown option.",
            parse_mode="HTML",
            reply_markup=get_main_menu_buttons(),
        )