"""
ShaunMariaOS

Scheduler Service
"""

from datetime import time
from zoneinfo import ZoneInfo

from telegram.error import TelegramError

from app_config import DEBUG, TELEGRAM_CHAT_ID
from apps.briefing_engine import get_daily_briefing
from utils.logger import logger


MORNING_BRIEFING_HOUR = 7
MORNING_BRIEFING_MINUTE = 30
TIMEZONE = ZoneInfo("Asia/Singapore")


async def send_morning_briefing(context):
    try:
        logger.info("Sending morning briefing...")
        logger.info(f"Sending to Chat ID: {TELEGRAM_CHAT_ID}")
        logger.info(f"Chat ID type: {type(TELEGRAM_CHAT_ID)}")

        await context.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=get_daily_briefing(),
            parse_mode="HTML",
        )

        logger.info("Morning briefing sent successfully.")

    except TelegramError as error:
        logger.error(f"Telegram error while sending morning briefing: {error}")

    except Exception as error:
        logger.error(f"Unexpected error while sending morning briefing: {error}")


def register_morning_briefing(application):
    if DEBUG:
        application.job_queue.run_repeating(
            send_morning_briefing,
            interval=60,
            first=10,
            name="morning_briefing_test",
        )
        logger.info("Morning briefing registered in DEBUG mode.")
    else:
        application.job_queue.run_daily(
            send_morning_briefing,
            time=time(
                hour=MORNING_BRIEFING_HOUR,
                minute=MORNING_BRIEFING_MINUTE,
                tzinfo=TIMEZONE,
            ),
            name="morning_briefing_daily",
        )
        logger.info("Morning briefing registered in PRODUCTION mode.")


def start_scheduler(application):
    if application.job_queue is None:
        logger.error("JobQueue unavailable.")
        return

    register_morning_briefing(application)
    logger.info("Scheduler started.")