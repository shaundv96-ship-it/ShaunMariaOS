"""
ShaunMariaOS

Calendar Handler
"""

from html import escape

from telegram import Update

from apps.calendar_engine import (
    create_calendar_event,
    parse_calendar_event,
)
from apps.menu_keyboard import get_persistent_main_keyboard
from utils.logger import logger


def format_time_12h(value) -> str:
    """Format a datetime as 12-hour time without a leading zero."""
    return value.strftime("%I:%M %p").lstrip("0")


async def handle_calendar(
    update: Update,
    text: str,
) -> None:
    """Parse and create a natural-language calendar event."""

    if not update.message:
        return

    parsed_event = parse_calendar_event(text)

    if parsed_event is None:
        await update.message.reply_text(
            (
                "⚠️ <b>Calendar Event Not Added</b>\n\n"
                "Please include both a date and time.\n\n"
                "Examples:\n"
                "<code>Dinner with Maria tmrw 7pm</code>\n"
                "<code>Meeting with Jane 3rd Aug at 7pm</code>"
            ),
            parse_mode="HTML",
            reply_markup=get_persistent_main_keyboard(),
        )
        return

    try:
        title = parsed_event["title"]
        start_time = parsed_event["start_time"]
        end_time = parsed_event["end_time"]

        created_event = create_calendar_event(
            title=title,
            start_time=start_time,
            end_time=end_time,
        )

        date_label = start_time.strftime(
            "%A, %d %B %Y"
        )

        time_label = (
            f"{format_time_12h(start_time)}"
            f" – "
            f"{format_time_12h(end_time)}"
        )

        calendar_link = created_event.get("htmlLink")

        message = (
            "✅ <b>Calendar Event Added</b>\n\n"
            f"📌 <b>{escape(title)}</b>\n\n"
            f"📅 {escape(date_label)}\n"
            f"🕒 {escape(time_label)}"
        )

        if calendar_link:
            message += (
                "\n\n"
                f'🔗 <a href="{escape(calendar_link, quote=True)}">'
                "Open in Google Calendar"
                "</a>"
            )

        await update.message.reply_text(
            message,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=get_persistent_main_keyboard(),
        )

    except Exception:
        logger.exception("Failed to create calendar event.")

        await update.message.reply_text(
            (
                "❌ <b>Calendar Event Not Added</b>\n\n"
                "Something went wrong while updating Google Calendar."
            ),
            parse_mode="HTML",
            reply_markup=get_persistent_main_keyboard(),
        )