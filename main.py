"""
Shaun&Maria OS
Version 0.3 - Telegram Command Bot
"""

from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from config import BOT_TOKEN


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = """❤️ <b>Shaun&Maria OS v0.3</b>

Commands:
/help - Show commands
/status - System status
/countdown - Wedding & BTO countdown"""
    await update.message.reply_text(message, parse_mode="HTML")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = """✅ <b>System Status</b>

Telegram Bot: Online
Python: Connected
Shaun&Maria OS: Running"""
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


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("countdown", countdown_command))

    print("❤️ Shaun&Maria OS v0.3 is running...")
    app.run_polling()


if __name__ == "__main__":
    main()