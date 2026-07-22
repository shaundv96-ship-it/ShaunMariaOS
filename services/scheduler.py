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
from apps.evening_engine import get_evening_wrap
from apps.weekly_review_engine import get_weekly_review
from apps.task_engine import get_open_tasks
from utils.logger import logger


MORNING_BRIEFING_HOUR = 7
MORNING_BRIEFING_MINUTE = 30

EVENING_TASK_HOUR = 18
EVENING_TASK_MINUTE = 0

EVENING_WRAP_HOUR = 21
EVENING_WRAP_MINUTE = 0

WEEKLY_REVIEW_HOUR = 20
WEEKLY_REVIEW_MINUTE = 0
WEEKLY_REVIEW_DAY = 6

TIMEZONE = ZoneInfo("Asia/Singapore")


async def send_morning_briefing(context):
    """Send the scheduled morning briefing."""

    try:
        logger.info("Sending morning briefing...")
        logger.info(
            "Sending morning briefing to Chat ID: "
            f"{TELEGRAM_CHAT_ID}"
        )

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

    Return None when there are no open tasks.
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
    """Send open-task reminders at 6:00 PM."""

    try:
        logger.info("Checking for open evening tasks...")

        message = get_evening_task_message()

        if message is None:
            logger.info(
                "No open tasks found. "
                "Evening task reminder not sent."
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


async def send_evening_wrap(context):
    """Send the nightly Evening Wrap."""

    try:
        logger.info("Sending Evening Wrap...")
        logger.info(
            "Sending Evening Wrap to Chat ID: "
            f"{TELEGRAM_CHAT_ID}"
        )

        await context.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=get_evening_wrap(),
            parse_mode="HTML",
        )

        logger.info("Evening Wrap sent successfully.")

    except TelegramError as error:
        logger.error(
            "Telegram error while sending Evening Wrap: "
            f"{error}"
        )

    except Exception:
        logger.exception(
            "Unexpected error while sending Evening Wrap."
        )


def register_morning_briefing(application):
    """Register the daily 7:30 AM morning briefing."""

    if DEBUG:
        logger.info(
            "DEBUG mode: Morning briefing scheduler disabled."
        )
        return

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
        "Morning briefing registered for "
        "7:30 AM Singapore time."
    )


def register_evening_task_reminder(application):
    """Register the daily 6:00 PM task reminder."""

    if DEBUG:
        logger.info(
            "DEBUG mode: Evening task reminder scheduler disabled."
        )
        return

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
        "Evening task reminder registered for "
        "6:00 PM Singapore time."
    )


def register_evening_wrap(application):
    """Register the daily 9:00 PM Evening Wrap."""

    if DEBUG:
        logger.info(
            "DEBUG mode: Evening Wrap scheduler disabled."
        )
        return

    application.job_queue.run_daily(
        send_evening_wrap,
        time=time(
            hour=EVENING_WRAP_HOUR,
            minute=EVENING_WRAP_MINUTE,
            tzinfo=TIMEZONE,
        ),
        name="evening_wrap_daily",
    )

    logger.info(
        "Evening Wrap registered for "
        "9:00 PM Singapore time."
    )


def start_scheduler(application):
    """Register all scheduled ShaunMariaOS jobs."""

    if application.job_queue is None:
        logger.error("JobQueue unavailable.")
        return

    register_morning_briefing(application)
    register_evening_task_reminder(application)
    register_evening_wrap(application)

    logger.info("Scheduler started.")

async def send_weekly_review(context):
    """Send the Sunday Weekly Review."""

    try:
        logger.info("Sending Weekly Review...")

        await context.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=get_weekly_review(),
            parse_mode="HTML",
        )

        logger.info("Weekly Review sent successfully.")

    except TelegramError as error:
        logger.error(
            "Telegram error while sending Weekly Review: "
            f"{error}"
        )

    except Exception:
        logger.exception(
            "Unexpected error while sending Weekly Review."
        )
def register_weekly_review(application):
    """Register the Sunday 8:00 PM Weekly Review."""

    if DEBUG:
        logger.info(
            "DEBUG mode: Weekly Review scheduler disabled."
        )
        return

    application.job_queue.run_daily(
        send_weekly_review,
        time=time(
            hour=WEEKLY_REVIEW_HOUR,
            minute=WEEKLY_REVIEW_MINUTE,
            tzinfo=TIMEZONE,
        ),
        days=(WEEKLY_REVIEW_DAY,),
        name="weekly_review_sunday",
    )

    logger.info(
        "Weekly Review registered for "
        "Sunday at 8:00 PM Singapore time."
    )

def start_scheduler(application):
    """Register all scheduled ShaunMariaOS jobs."""

    if application.job_queue is None:
        logger.error("JobQueue unavailable.")
        return

    register_morning_briefing(application)
    register_evening_task_reminder(application)
    register_evening_wrap(application)
    register_weekly_review(application)

    logger.info("Scheduler started.")