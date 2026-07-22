"""
ShaunMariaOS

Main Telegram Bot Application
"""

from datetime import datetime
from html import escape

from telegram import InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app_config import APP_NAME
from apps.about_engine import get_about
from apps.bills_engine import get_bills_dashboard
from apps.briefing_engine import get_daily_briefing
from apps.evening_engine import get_evening_wrap
from apps.calendar_engine import (
    format_today_events_for_telegram,
    format_tomorrow_events_for_telegram,
)
from apps.changelog_engine import get_changelog_dashboard
from apps.dashboard_engine import get_dashboard_message
from apps.database_engine import get_database_status
from apps.expense_engine import (
    ExpenseEntry,
    format_expense_confirmation,
    parse_expense_command,
    save_expense,
)
from apps.expense_summary_engine import get_expense_dashboard
from apps.finance_engine import get_finance_dashboard
from apps.health_engine import get_health
from apps.insurance_engine import get_insurance_dashboard
from apps.intent_engine import detect_intent
from apps.menu_keyboard import (
    get_main_menu_buttons,
    get_money_menu_buttons,
    get_persistent_main_keyboard,
    get_system_menu_buttons,
    get_wedding_menu_buttons,
)
from apps.money_engine import get_money_dashboard

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
from handlers.expense_handler import handle_expense
from handlers.income_handler import handle_income
from services.scheduler import start_scheduler
from utils.error_handler import error_handler
from utils.logger import logger
from utils.startup import startup_banner
from utils.time import sg_now

from handlers.expense_handler import handle_expense
from handlers.income_handler import handle_income
from handlers.task_handler import handle_task
from handlers.unknown_handler import handle_unknown
from handlers.wedding_handler import handle_wedding
from handlers.task_handler import (
    get_tasks_message,
    handle_task,
)

async def reply_with_main_keyboard(update: Update, message: str) -> None:
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


async def save_and_confirm_expense(
    update: Update,
    expense: ExpenseEntry,
) -> None:
    """Save a structured /expense entry and send confirmation."""
    save_expense(expense)
    await reply_with_main_keyboard(
        update,
        format_expense_confirmation(expense),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = f"""❤️ <b>{APP_NAME}</b>

<b>Main</b>
/menu - Easy menu
/dashboard - Main dashboard
/briefing - Daily briefing
/evening - Evening wrap
/notifications - Active notifications

<b>Wedding</b>
/wedding - Wedding dashboard
/weddingbudget - Wedding budget
/guestlist - Guestlist summary
/timeline - Wedding timeline

<b>Money</b>
/money - MoneyOS dashboard
/finance - Finance details
/salary - Salary
/bills - Bills
/insurance - Insurance
/expense - Add expense
/expenses - Expense summary

<b>Calendar</b>
/today - Today's schedule
/tomorrow - Tomorrow's schedule
/task

<b>System</b>
/status - System status
/database - Database status
/health - System health
/version - Version
/about - About ShaunMariaOS
/changelog - Release history"""
    await reply_with_main_keyboard(update, message)


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_with_main_keyboard(
        update,
        f"❤️ <b>{APP_NAME}</b>\n\nChoose an option below 👇",
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = f"""✅ <b>System Status</b>

🤖 Telegram Bot
Online

🐍 Python
Connected

📅 Google Calendar
Connected

📊 Google Sheets
Connected

❤️ {APP_NAME}
Running"""
    await reply_with_main_keyboard(update, message)


async def countdown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    today = sg_now().date()
    wedding_date = datetime(2026, 10, 31).date()
    wedding_days = (wedding_date - today).days
    message = f"""❤️ <b>Shaun & Maria Countdown</b>

💒 <b>Wedding</b>
{wedding_days} days to go

🏠 <b>BTO</b>
Estimated TOP: Q3 2030"""
    await reply_with_main_keyboard(update, message)


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_with_main_keyboard(update, format_today_events_for_telegram())


async def tomorrow_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_with_main_keyboard(update, format_tomorrow_events_for_telegram())


async def dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_with_main_keyboard(update, get_dashboard_message())


async def briefing_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_with_main_keyboard(update, get_daily_briefing())

async def evening_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await reply_with_main_keyboard(
        update,
        get_evening_wrap(),
    )

async def notifications_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_with_main_keyboard(update, get_notification_message())


async def database_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_with_main_keyboard(update, get_database_status())


async def wedding_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_with_inline_keyboard(
        update,
        get_wedding_dashboard(),
        get_wedding_menu_buttons(),
    )


async def wedding_budget_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_with_inline_keyboard(
        update,
        get_wedding_budget(),
        get_wedding_menu_buttons(),
    )


async def guestlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_with_inline_keyboard(
        update,
        get_guestlist_summary(),
        get_wedding_menu_buttons(),
    )


async def timeline_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_with_inline_keyboard(
        update,
        get_wedding_timeline(),
        get_wedding_menu_buttons(),
    )


async def finance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_with_inline_keyboard(
        update,
        get_finance_dashboard(),
        get_money_menu_buttons(),
    )

async def tasks_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Show all open tasks."""

    try:
        message = get_tasks_message()

    except Exception:
        logger.exception("Failed to load open tasks.")

        message = (
            "⚠️ <b>Tasks Unavailable</b>\n\n"
            "Something went wrong while reading the Tasks sheet."
        )

    await reply_with_main_keyboard(
        update,
        message,
    )

async def salary_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_with_inline_keyboard(
        update,
        get_salary_dashboard(),
        get_money_menu_buttons(),
    )


async def bills_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_with_inline_keyboard(
        update,
        get_bills_dashboard(),
        get_money_menu_buttons(),
    )


async def insurance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_with_inline_keyboard(
        update,
        get_insurance_dashboard(),
        get_money_menu_buttons(),
    )


async def expense_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add an expense through the structured /expense command."""
    try:
        expense = parse_expense_command(context.args)
        await save_and_confirm_expense(update, expense)

    except ValueError as error:
        await reply_with_main_keyboard(
            update,
            f"""⚠️ <b>Expense Not Added</b>

{escape(str(error))}""",
        )

    except Exception:
        logger.exception("Failed to add expense.")
        await reply_with_main_keyboard(
            update,
            """⚠️ <b>Expense Not Added</b>

Something went wrong while updating Google Sheets.""",
        )
async def expenses_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the monthly Expense Log summary."""
    try:
        message = get_expense_dashboard()
    except Exception:
        logger.exception("Failed to load expense summary.")
        message = """⚠️ <b>Expense Summary Unavailable</b>

Something went wrong while reading the Expense Log."""
    await reply_with_main_keyboard(update, message)

async def money_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_with_inline_keyboard(
        update,
        get_money_dashboard(),
        get_money_menu_buttons(),
    )

async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_with_inline_keyboard(
        update,
        get_health(),
        get_system_menu_buttons(),
    )


async def version_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_with_inline_keyboard(
        update,
        get_version(),
        get_system_menu_buttons(),
    )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_with_inline_keyboard(
        update,
        get_about(),
        get_system_menu_buttons(),
    )


async def changelog_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_with_main_keyboard(update, get_changelog_dashboard())


async def chatid_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat:
        return
    await reply_with_main_keyboard(
        update,
        f"Your Chat ID is:\n\n{update.effective_chat.id}",
    )


async def text_button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle menu buttons and natural-language messages."""

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

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
            get_money_dashboard,
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

    if route:
        message_source, keyboard_source = route

        await update.message.reply_text(
            message_source(),
            parse_mode="HTML",
            reply_markup=keyboard_source(),
        )
        return

    # This line must be outside the route block.
    intent = detect_intent(text)

    intent_handlers = {
        "expense": handle_expense,
        "income": handle_income,
        "wedding": handle_wedding,
        "task": handle_task,
    }

    handler = intent_handlers.get(
        intent.name,
        handle_unknown,
    )

    await handler(
        update,
        text,
    )
def register_handlers(app) -> None:
    """Register Telegram command, text, callback, and error handlers."""
    command_handlers = {
        "help": help_command,
        "menu": menu_command,
        "status": status_command,
        "database": database_command,
        "countdown": countdown_command,
        "today": today_command,
        "tomorrow": tomorrow_command,
        "dashboard": dashboard_command,
        "briefing": briefing_command,
        "evening": evening_command,
        "notifications": notifications_command,
        "wedding": wedding_command,
        "weddingbudget": wedding_budget_command,
        "guestlist": guestlist_command,
        "timeline": timeline_command,
        "money": money_command,
        "finance": finance_command,
        "salary": salary_command,
        "bills": bills_command,
        "insurance": insurance_command,
        "expense": expense_command,
        "expenses": expenses_command,
        "health": health_command,
        "version": version_command,
        "about": about_command,
        "changelog": changelog_command,
        "chatid": chatid_command,
        "tasks": tasks_command,
        
    }

    for command, callback in command_handlers.items():
        app.add_handler(CommandHandler(command, callback))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_button_handler,
        )
    )
    app.add_handler(CallbackQueryHandler(handle_menu_button))
    app.add_error_handler(error_handler)


def main() -> None:
    """Start ShaunMariaOS."""
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