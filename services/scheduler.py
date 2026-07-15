"""
ShaunMariaOS

Scheduler Service
"""

from datetime import time
from html import escape
from zoneinfo import ZoneInfo

from telegram.error import TelegramError

from app_config import DEBUG, TELEGRAM_CHAT_ID
from apps.briefing_engine import get_daily_briefing
from apps.task_engine import get_open_tasks
from utils.logger import logger


MORNING_BRIEFING_HOUR = 7
MORNING_BRIEFING_MINUTE = 30

EVENING_TASK_HOUR = 18
EVENING_TASK_MINUTE = 0

TIMEZONE = ZoneInfo("Asia/Singapore")


async def send_morning_briefing(context):
    """Send the scheduled morning briefing."""

    try:
        logger.info("Sending morning briefing...")
        logger.info(f"Sending to Chat ID: {TELEGRAM_CHAT_ID}")

        await context.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=get_daily_briefing(),
            parse_mode="HTML",
        )

        logger.info("Morning briefing sent successfully.")

    except TelegramError as error:
        logger.error(
            "Telegram error while sending morning briefing: "
            f"{error}"
        )

    except Exception:
        logger.exception(
            "Unexpected error while sending morning briefing."
        )


def get_evening_task_message() -> str | None:
    """
    Build the evening task reminder.

    Returns None when there are no open tasks.
    """

    tasks = get_open_tasks()

    if not tasks:
        return None

    sections = [
        "🌆 <b>Evening Task Reminder</b>",
        "\n\nYou still have open tasks:",
    ]

    for task in tasks:
        task_text = escape(task["task"])
        owner = escape(task["owner"])
        priority = escape(task["priority"])

        sections.append(
            f"\n\n<b>{task['id']}. {task_text}</b>"
            f"\n👤 {owner}"
            f"\n📌 {priority}"
        )

        if task["due_date"]:
            sections.append(
                f"\n📅 {escape(task['due_date'])}"
            )

    sections.append(
        "\n\nComplete a task with:"
        "\n<code>Done 1</code>"
    )

    return "".join(sections)


async def send_evening_task_reminder(context):
    """Send open-task reminders at 6 PM."""

    try:
        logger.info("Checking for open evening tasks...")

        message = get_evening_task_message()

        if message is None:
            logger.info(
                "No open tasks found. "
                "Evening reminder not sent."
            )
            return

        await context.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode="HTML",
        )

        logger.info(
            "Evening task reminder sent successfully."
        )

    except TelegramError as error:
        logger.error(
            "Telegram error while sending task reminder: "
            f"{error}"
        )

    except Exception:
        logger.exception(
            "Unexpected error while sending task reminder."
        )


def register_morning_briefing(application):
    """Register the daily morning briefing."""

    if DEBUG:
        application.job_queue.run_repeating(
            send_morning_briefing,
            interval=60,
            first=10,
            name="morning_briefing_test",
        )

        logger.info(
            "Morning briefing registered in DEBUG mode."
        )

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

        logger.info(
            "Morning briefing registered in PRODUCTION mode."
        )


def register_evening_task_reminder(application):
    """Register the daily 6 PM task reminder."""

    if DEBUG:
        application.job_queue.run_repeating(
            send_evening_task_reminder,
            interval=60,
            first=20,
            name="evening_task_reminder_test",
        )

        logger.info(
            "Evening task reminder registered in DEBUG mode."
        )

    else:
        application.job_queue.run_daily(
            send_evening_task_reminder,
            time=time(
                hour=EVENING_TASK_HOUR,
                minute=EVENING_TASK_MINUTE,
                tzinfo=TIMEZONE,
            ),
            name="evening_task_reminder_daily",
        )

        logger.info(
            "Evening task reminder registered "
            "for 6:00 PM Singapore time."
        )


def start_scheduler(application):
    """Register all scheduled ShaunMariaOS jobs."""

    if application.job_queue is None:
        logger.error("JobQueue unavailable.")
        return

    register_morning_briefing(application)
    register_evening_task_reminder(application)

    logger.info("Scheduler started.")