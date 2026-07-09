"""
ShaunMariaOS
Main Telegram Bot Application
"""

from datetime import datetime

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from utils.time import sg_now
from config import BOT_TOKEN, write_google_auth_files
from apps.about_engine import get_about
from apps.bills_engine import get_bills_dashboard
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
from apps.menu_keyboard import get_main_menu_buttons
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
from apps.briefing_engine import get_daily_briefing
from services.scheduler import start_scheduler
from utils.error_handler import error_handler
from utils.logger import logger
from utils.startup import startup_banner


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = """❤️ <b>ShaunMariaOS</b>

Main:
/menu - Easy menu
/dashboard - Main dashboard
/briefing - Daily briefing

Wedding:
/wedding - Wedding dashboard
/weddingbudget - Wedding budget
/guestlist - Guestlist summary
/timeline - Wedding timeline

Money:
/finance - Finance dashboard
/salary - Salary dashboard
/bills - Monthly bills
/insurance - Insurance dashboard

Calendar:
/today - Today's schedule
/tomorrow - Tomorrow's schedule

System:
/status - System status
/health - System health
/version - Version
/about - About ShaunMariaOS
/changelog - Release history"""
    await update.message.reply_text(message, parse_mode="HTML")


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❤️ <b>ShaunMariaOS</b>\n\nChoose an option below 👇",
        parse_mode="HTML",
        reply_markup=get_main_menu_buttons(),
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = """✅ <b>System Status</b>

Telegram Bot: Online
Python: Connected
Google Calendar: Connected
Google Sheets: Connected
ShaunMariaOS: Running"""
    await update.message.reply_text(message, parse_mode="HTML")


async def countdown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
   today = sg_now().date()
wedding_date = datetime(2026, 10, 31).date()
wedding_days = (wedding_date - today).days

    message = f"""❤️ <b>Shaun & Maria Countdown</b>

💒 Wedding:
{wedding_days} days to go

🏠 BTO:
Estimated TOP: Q3 2030"""
    await update.message.reply_text(message, parse_mode="HTML")


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        format_today_events_for_telegram(),
        parse_mode="HTML",
    )


async def tomorrow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        format_tomorrow_events_for_telegram(),
        parse_mode="HTML",
    )


async def dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        get_dashboard_message(),
        parse_mode="HTML",
    )


async def database_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        get_database_status(),
        parse_mode="HTML",
    )


async def wedding_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        get_wedding_dashboard(),
        parse_mode="HTML",
    )


async def wedding_budget_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        get_wedding_budget(),
        parse_mode="HTML",
    )


async def guestlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        get_guestlist_summary(),
        parse_mode="HTML",
    )


async def timeline_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        get_wedding_timeline(),
        parse_mode="HTML",
    )


async def finance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        get_finance_dashboard(),
        parse_mode="HTML",
    )


async def bills_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        get_bills_dashboard(),
        parse_mode="HTML",
    )


async def salary_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        get_salary_dashboard(),
        parse_mode="HTML",
    )


async def insurance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        get_insurance_dashboard(),
        parse_mode="HTML",
    )


async def briefing_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        get_daily_briefing(),
        parse_mode="HTML",
    )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        get_about(),
        parse_mode="HTML",
    )


async def notifications_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        get_notification_message(),
        parse_mode="HTML",
    )


async def changelog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        get_changelog_dashboard(),
        parse_mode="HTML",
    )


async def chatid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Your Chat ID is:\n\n{update.effective_chat.id}"
    )


async def version_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        get_version(),
        parse_mode="HTML",
    )


async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        get_health(),
        parse_mode="HTML",
    )

async def text_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📅 Today":
        message = format_today_events_for_telegram()
    elif text == "💍 Wedding":
        message = get_wedding_dashboard()
    elif text == "💰 Money":
        message = get_finance_dashboard()
    elif text == "❤️ Dashboard":
        message = get_dashboard_message()
    elif text == "🏠 Home":
        message = "🏠 <b>HomeOS</b>\n\nComing soon."
    elif text == "⚙️ More":
        message = get_health()
    else:
        return

    await update.message.reply_text(message, parse_mode="HTML")


def register_handlers(app):
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("database", database_command))
    app.add_handler(CommandHandler("countdown", countdown_command))
    app.add_handler(CommandHandler("today", today_command))
    app.add_handler(CommandHandler("tomorrow", tomorrow_command))
    app.add_handler(CommandHandler("dashboard", dashboard_command))
    app.add_handler(CommandHandler("wedding", wedding_command))
    app.add_handler(CommandHandler("weddingbudget", wedding_budget_command))
    app.add_handler(CommandHandler("guestlist", guestlist_command))
    app.add_handler(CommandHandler("timeline", timeline_command))
    app.add_handler(CommandHandler("finance", finance_command))
    app.add_handler(CommandHandler("bills", bills_command))
    app.add_handler(CommandHandler("salary", salary_command))
    app.add_handler(CommandHandler("insurance", insurance_command))
    app.add_handler(CommandHandler("briefing", briefing_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("notifications", notifications_command))
    app.add_handler(CommandHandler("changelog", changelog_command))
    app.add_handler(CommandHandler("chatid", chatid_command))
    app.add_handler(CommandHandler("version", version_command))
    app.add_handler(CommandHandler("health", health_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_button_handler))

    app.add_handler(CallbackQueryHandler(handle_menu_button))
    app.add_error_handler(error_handler)


def main():
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