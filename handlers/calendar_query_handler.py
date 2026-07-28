"""
ShaunMariaOS

Calendar Query Handler
"""

from html import escape

from telegram import Update

from apps.calendar_engine import (
    format_calendar_event,
    get_events_for_date,
    get_next_calendar_event,
    resolve_calendar_query_date,
)
from apps.menu_keyboard import get_persistent_main_keyboard
from utils.logger import logger


async def handle_calendar_query(
    update: Update,
    text: str,
) -> None:
    """Handle natural-language calendar questions."""

    if not update.message:
        return

    normalized = text.lower().strip()

    try:
        if "next meeting" in normalized:
            event = get_next_calendar_event()

            if not event:
                message = (
                    "📅 <b>Next Event</b>\n\n"
                    "You have no upcoming calendar events."
                )

            else:
                event_text = format_calendar_event(event)

                message = (
                    "📅 <b>Next Event</b>\n\n"
                    f"{escape(event_text)}"
                )

            await update.message.reply_text(
                message,
                parse_mode="HTML",
                reply_markup=get_persistent_main_keyboard(),
            )
            return

        target_date = resolve_calendar_query_date(text)

        if target_date is None:
            await update.message.reply_text(
                (
                    "⚠️ <b>Calendar Query Not Understood</b>\n\n"
                    "Try:\n"
                    "<code>What's on tomorrow?</code>\n"
                    "<code>Am I free Friday?</code>\n"
                    "<code>Next meeting</code>"
                ),
                parse_mode="HTML",
                reply_markup=get_persistent_main_keyboard(),
            )
            return

        events = get_events_for_date(target_date)

        date_label = target_date.strftime(
            "%A, %d %B %Y"
        )

        if "free" in normalized:
            if events:
                event_lines = "\n".join(
                    escape(format_calendar_event(event))
                    for event in events
                )

                message = (
                    f"📅 <b>{escape(date_label)}</b>\n\n"
                    "You already have:\n\n"
                    f"{event_lines}"
                )

            else:
                message = (
                    f"✅ <b>{escape(date_label)}</b>\n\n"
                    "Your calendar is clear."
                )

        else:
            if events:
                event_lines = "\n".join(
                    escape(format_calendar_event(event))
                    for event in events
                )

                message = (
                    f"📅 <b>{escape(date_label)}</b>\n\n"
                    f"{event_lines}"
                )

            else:
                message = (
                    f"📅 <b>{escape(date_label)}</b>\n\n"
                    "No events scheduled."
                )

        await update.message.reply_text(
            message,
            parse_mode="HTML",
            reply_markup=get_persistent_main_keyboard(),
        )

    except Exception:
        logger.exception("Failed to process calendar query.")

        await update.message.reply_text(
            (
                "❌ <b>Calendar Query Failed</b>\n\n"
                "Something went wrong while reading Google Calendar."
            ),
            parse_mode="HTML",
            reply_markup=get_persistent_main_keyboard(),
        )