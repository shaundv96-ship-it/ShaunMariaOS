"""
ShaunMariaOS

Main Telegram Bot Application
"""

from datetime import datetime

from telegram import InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from apps.about_engine import get_about
from apps.bills_engine import get_bills_dashboard
from apps.briefing_engine import get_daily_briefing
from apps.calendar_engine import (
    format_today_events_for_telegram,
    format_tomorrow_events_for_telegram,
)
from apps.changelog_engine import get_changelog_dashboard
from apps.dashboard_engine import get_dashboard_message
from apps.database_engine import get_database_status
from apps.finance_engine import get_finance_dashboard
from apps.health_engine import get_health
from apps.insurance_engine import get_insurance_dashboard
from apps.menu_keyboard import (
    get_main_menu_buttons,
    get_money_menu_buttons,
    get_persistent_main_keyboard,
    get_system_menu_buttons,
    get_wedding_menu_buttons,
)
from apps.expense_engine import (
    format_expense_confirmation,
    parse_expense_command,
    save_expense,
)
from apps.menu_navigation import handle_menu_button
from apps.notification_engine import get_notification_message
from apps.salary_engine import get_salary_dashboard
from apps.version_engine import get_version
from apps.wedding_engine import (
    get_guestlist_summary,
    get_wedding_budget,
    get_wedding_dashboard,
    get_wedding_timeline,
)
from config import BOT_TOKEN, write_google_auth_files
from services.scheduler import start_scheduler
from utils.error_handler import error_handler
from utils.logger import logger
from utils.startup import startup_banner
from utils.time import sg_now


# ====================================================
# Shared Telegram Reply Helpers
# ====================================================

async def reply_with_main_keyboard(
    update: Update,
    message: str,
) -> None:
    """Reply while restoring the persistent bottom keyboard."""
    if not update.message:
        return

    await update.message.reply_text(
        message,
        parse_mode="HTML",
        reply_markup=get_persistent_main_keyboard(),
    )


async def reply_with_inline_keyboard(
    update: Update,
    message: str,
    keyboard: InlineKeyboardMarkup,
) -> None:
    """Reply with an inline submenu."""
    if not update.message:
        return

    await update.message.reply_text(
        message,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


# ====================================================
# Main Commands
# ====================================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    message = """❤️ <b>ShaunMariaOS</b>

<b>Main</b>
/menu - Easy menu
/dashboard - Main dashboard
/briefing - Daily briefing
/notifications - Active notifications


<b>Wedding</b>
/wedding - Wedding dashboard
/weddingbudget - Wedding budget
/guestlist - Guestlist summary
/timeline - Wedding timeline

<b>Money</b>
/finance - Finance dashboard
/salary - Salary dashboard
/bills - Monthly bills
/insurance - Insurance dashboard
/expense - Add an expense

<b>Calendar</b>
/today - Today's schedule
/tomorrow - Tomorrow's schedule

<b>System</b>
/status - System status
/database - Database status
/health - System health
/version - Version
/about - About ShaunMariaOS
/changelog - Release history"""

    await reply_with_main_keyboard(update, message)


async def menu_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await reply_with_main_keyboard(
        update,
        "❤️ <b>ShaunMariaOS</b>\n\nChoose an option below 👇",
    )


async def status_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    message = """✅ <b>System Status</b>

🤖 Telegram Bot
Online

🐍 Python
Connected

📅 Google Calendar
Connected

📊 Google Sheets
Connected

❤️ ShaunMariaOS
Running"""

    await reply_with_main_keyboard(update, message)


async def countdown_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    today = sg_now().date()
    wedding_date = datetime(2026, 10, 31).date()
    wedding_days = (wedding_date - today).days

    message = f"""❤️ <b>Shaun & Maria Countdown</b>

💒 <b>Wedding</b>
{wedding_days} days to go

🏠 <b>BTO</b>
Estimated TOP: Q3 2030"""

    await reply_with_main_keyboard(update, message)


async def today_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await reply_with_main_keyboard(
        update,
        format_today_events_for_telegram(),
    )


async def tomorrow_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await reply_with_main_keyboard(
        update,
        format_tomorrow_events_for_telegram(),
    )


async def dashboard_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await reply_with_main_keyboard(
        update,
        get_dashboard_message(),
    )


async def briefing_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await reply_with_main_keyboard(
        update,
        get_daily_briefing(),
    )


async def notifications_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await reply_with_main_keyboard(
        update,
        get_notification_message(),
    )


async def database_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await reply_with_main_keyboard(
        update,
        get_database_status(),
    )
async def expense_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    try:
        expense = parse_expense_command(context.args)
        save_expense(expense)

        message = format_expense_confirmation(expense)

    except ValueError as error:
        message = f"""⚠️ <b>Expense Not Added</b>

{error}"""

    except Exception:
        logger.exception("Failed to add expense.")

        message = """⚠️ <b>Expense Not Added</b>

Something went wrong while updating Google Sheets."""

    await reply_with_main_keyboard(
        update,
        message,
    )

# ====================================================
# Wedding Commands
# ====================================================

async def wedding_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await reply_with_inline_keyboard(
        update,
        get_wedding_dashboard(),
        get_wedding_menu_buttons(),
    )


async def wedding_budget_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await reply_with_inline_keyboard(
        update,
        get_wedding_budget(),
        get_wedding_menu_buttons(),
    )


async def guestlist_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await reply_with_inline_keyboard(
        update,
        get_guestlist_summary(),
        get_wedding_menu_buttons(),
    )


async def timeline_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await reply_with_inline_keyboard(
        update,
        get_wedding_timeline(),
        get_wedding_menu_buttons(),
    )


# ====================================================
# Finance Commands
# ====================================================

async def finance_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await reply_with_inline_keyboard(
        update,
        get_finance_dashboard(),
        get_money_menu_buttons(),
    )


async def salary_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await reply_with_inline_keyboard(
        update,
        get_salary_dashboard(),
        get_money_menu_buttons(),
    )


async def bills_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await reply_with_inline_keyboard(
        update,
        get_bills_dashboard(),
        get_money_menu_buttons(),
    )


async def insurance_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await reply_with_inline_keyboard(
        update,
        get_insurance_dashboard(),
        get_money_menu_buttons(),
    )


# ====================================================
# System Commands
# ====================================================

async def health_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await reply_with_inline_keyboard(
        update,
        get_health(),
        get_system_menu_buttons(),
    )


async def version_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await reply_with_inline_keyboard(
        update,
        get_version(),
        get_system_menu_buttons(),
    )


async def about_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await reply_with_inline_keyboard(
        update,
        get_about(),
        get_system_menu_buttons(),
    )


async def changelog_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await reply_with_main_keyboard(
        update,
        get_changelog_dashboard(),
    )


async def chatid_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await reply_with_main_keyboard(
        update,
        f"Your Chat ID is:\n\n{update.effective_chat.id}",
    )


# ====================================================
# Persistent Bottom Keyboard Handler
# ====================================================

async def text_button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message:
        return

    text = update.message.text

    routes = {
        "📅 Today": (
            format_today_events_for_telegram,
            get_main_menu_buttons,
        ),
        "💍 Wedding": (
            get_wedding_dashboard,
            get_wedding_menu_buttons,
        ),
        "💰 Money": (
            get_finance_dashboard,
            get_money_menu_buttons,
        ),
        "❤️ Dashboard": (
            get_dashboard_message,
            get_main_menu_buttons,
        ),
        "🏠 Home": (
            lambda: "🏠 <b>HomeOS</b>\n\nComing later.",
            get_main_menu_buttons,
        ),
        "⚙️ More": (
            get_health,
            get_system_menu_buttons,
        ),
    }

    route = routes.get(text)

    if not route:
        return

    message_source, keyboard_source = route

    await update.message.reply_text(
        message_source(),
        parse_mode="HTML",
        reply_markup=keyboard_source(),
    )


# ====================================================
# Handler Registration
# ====================================================

def register_handlers(app) -> None:
    command_handlers = {
        "help": help_command,
        "menu": menu_command,
        "status": status_command,
        "database": database_command,
        "countdown": countdown_command,
        "today": today_command,
        "tomorrow": tomorrow_command,
        "dashboard": dashboard_command,
        "wedding": wedding_command,
        "weddingbudget": wedding_budget_command,
        "guestlist": guestlist_command,
        "timeline": timeline_command,
        "finance": finance_command,
        "salary": salary_command,
        "bills": bills_command,
        "insurance": insurance_command,
        "briefing": briefing_command,
        "notifications": notifications_command,
        "about": about_command,
        "changelog": changelog_command,
        "chatid": chatid_command,
        "version": version_command,
        "health": health_command,
        "expense": expense_command,
    }

    for command, callback in command_handlers.items():
        app.add_handler(CommandHandler(command, callback))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_button_handler,
        )
    )

    app.add_handler(
        CallbackQueryHandler(handle_menu_button)
    )

    app.add_error_handler(error_handler)


# ====================================================
# Application Startup
# ====================================================

def main() -> None:
    logger.info("Starting ShaunMariaOS...")

    write_google_auth_files()
    logger.info("Google auth files prepared.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    logger.info("Telegram bot initialized.")

    register_handlers(app)
    start_scheduler(app)

    startup_banner()
    app.run_polling()


if __name__ == "__main__":
    main()