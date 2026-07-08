"""
ShaunMariaOS
Main Telegram Bot Application
"""

from datetime import datetime

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from config import BOT_TOKEN
from apps.calendar_engine import (
    format_today_events_for_telegram,
    format_tomorrow_events_for_telegram,
)
from apps.dashboard_engine import get_dashboard_message
from apps.database_engine import get_database_status
from apps.wedding_engine import (
    get_wedding_dashboard,
    get_wedding_budget,
    get_guestlist_summary,
    get_wedding_timeline,
)
from apps.database_engine import get_database_status
from apps.finance_engine import get_finance_dashboard
from apps.bills_engine import get_bills_dashboard
from apps.salary_engine import get_salary_dashboard
from apps.insurance_engine import get_insurance_dashboard
from apps.briefing_engine import get_daily_briefing
from apps.about_engine import get_about
from utils.logger import logger
from apps.notification_engine import get_notification_message
from apps.changelog_engine import get_changelog_dashboard
from services.scheduler import start_scheduler
from config import write_google_auth_files
from apps.version_engine import get_version
from apps.health_engine import get_health
from utils.startup import startup_banner

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = """❤️ <b>ShaunMariaOS</b>

Commands:
/help - Show commands
/status - System status
/database - Database status
/countdown - Wedding & BTO countdown
/today - Today's schedule
/tomorrow - Tomorrow's schedule
/wedding - Wedding dashboard
/weddingbudget - Wedding budget
/guestlist - Guestlist summary
/timeline - Wedding timeline
/finance - Finance dashboard
/bills - Monthly bills
/salary - Salary dashboard
/insurance - Insurance dashboard
/briefing - Daily briefing
/about - About ShaunMariaOS
/changelog - View release history
/notifications - Smart reminders
/health - System health
/dashboard - Main dashboard"""
    await update.message.reply_text(message, parse_mode="HTML")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = """✅ <b>System Status</b>

Telegram Bot: Online
Python: Connected
Google Calendar: Connected
Google Sheets: Connected
ShaunMariaOS: Running"""
    await update.message.reply_text(message, parse_mode="HTML")


async def countdown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now()
    wedding_date = datetime(2026, 10, 31)
    wedding_days = (wedding_date - today).days

    message = f"""❤️ <b>Shaun & Maria Countdown</b>

💒 Wedding:
{wedding_days} days to go

🏠 BTO:
Estimated TOP: Q3 2030"""
    await update.message.reply_text(message, parse_mode="HTML")


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = format_today_events_for_telegram()
    await update.message.reply_text(message, parse_mode="HTML")


async def tomorrow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = format_tomorrow_events_for_telegram()
    await update.message.reply_text(message, parse_mode="HTML")


async def dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = get_dashboard_message()
    await update.message.reply_text(message, parse_mode="HTML")


async def database_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = get_database_status()
    await update.message.reply_text(message, parse_mode="HTML")


async def wedding_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = get_wedding_dashboard()
    await update.message.reply_text(message, parse_mode="HTML")


async def wedding_budget_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = get_wedding_budget()
    await update.message.reply_text(message, parse_mode="HTML")

async def guestlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = get_guestlist_summary()
    await update.message.reply_text(message, parse_mode="HTML")

async def timeline_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = get_wedding_timeline()
    await update.message.reply_text(message, parse_mode="HTML")
async def finance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = get_finance_dashboard()

    await update.message.reply_text(
        message,
        parse_mode="HTML"
    )
async def bills_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = get_bills_dashboard()

    await update.message.reply_text(
        message,
        parse_mode="HTML"
    )
async def salary_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = get_salary_dashboard()

    await update.message.reply_text(
        message,
        parse_mode="HTML"
    )
async def insurance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = get_insurance_dashboard()

    await update.message.reply_text(
        message,
        parse_mode="HTML"
    )
async def briefing_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = get_daily_briefing()
    await update.message.reply_text(message, parse_mode="HTML")
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):await update.message.reply_text(get_about(),parse_mode="HTML",)
async def notifications_command(update, context):await update.message.reply_text(get_notification_message(),parse_mode="HTML",)
async def changelog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):await update.message.reply_text(get_changelog_dashboard(),parse_mode="HTML",)
async def chatid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):await update.message.reply_text(f"Your Chat ID is:\n\n{update.effective_chat.id}")
async def version_command(update, context):await update.message.reply_text(get_version(),parse_mode="HTML",)
async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE):await update.message.reply_text(get_health(), parse_mode="HTML")

def main():
    """
    Entry point for ShaunMariaOS.
    Initializes Telegram, registers commands, starts scheduler and polling.
    """
    logger.info("Starting ShaunMariaOS...")

    write_google_auth_files()
    logger.info("Google auth files prepared.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    logger.info("Telegram bot initialized.")

    from app_config import TELEGRAM_CHAT_ID

    

    app.add_handler(CommandHandler("help", help_command))
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

    start_scheduler(app)
    from utils.error_handler import error_handler

    app.add_error_handler(error_handler)

    startup_banner()
    app.run_polling()


if __name__ == "__main__":
    main()