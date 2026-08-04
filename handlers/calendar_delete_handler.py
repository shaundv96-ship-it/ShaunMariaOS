"""
ShaunMariaOS

Calendar Delete Handler
"""

import re
from html import escape

from telegram import Update

from apps.calendar_engine import (
    delete_calendar_series,
    get_event_date_label,
    is_recurring_calendar_event,
    search_calendar_series,
)
from apps.menu_keyboard import get_persistent_main_keyboard
from utils.logger import logger


def parse_calendar_delete_query(
    text: str,
) -> str:
    """Extract the event title from a deletion request."""

    query = re.sub(
        r"^\s*(?:cancel|delete|remove)\s+",
        "",
        text,
        flags=re.IGNORECASE,
    )

    return query.strip(
        " ."
    )


async def handle_calendar_delete(
    update: Update,
    text: str,
) -> None:
    """Find and safely delete one Calendar event or series."""

    if not update.message:
        return

    search_text = parse_calendar_delete_query(
        text
    )

    if not search_text:
        await update.message.reply_text(
            (
                "⚠️ <b>Event Not Deleted</b>\n\n"
                "Tell me which event to remove.\n\n"
                "Example:\n"
                "<code>Cancel JB trip</code>"
            ),
            parse_mode="HTML",
            reply_markup=get_persistent_main_keyboard(),
        )
        return

    try:
        events = search_calendar_series(
            search_text
        )

        if not events:
            await update.message.reply_text(
                (
                    "🔎 <b>Event Not Found</b>\n\n"
                    "I couldn't find an upcoming event matching "
                    f"<b>{escape(search_text)}</b>."
                ),
                parse_mode="HTML",
                reply_markup=get_persistent_main_keyboard(),
            )
            return

        if len(events) > 1:
            lines = [
                "⚠️ <b>More Than One Event Found</b>",
                "",
                "Nothing was deleted. I found:",
            ]

            for event in events[:5]:
                title = escape(
                    event.get(
                        "summary",
                        "Untitled Event",
                    )
                )

                date_label = escape(
                    get_event_date_label(
                        event
                    )
                )

                recurrence_label = (
                    " — Recurring"
                    if is_recurring_calendar_event(event)
                    else ""
                )

                lines.append(
                    f"\n• <b>{title}</b>"
                    f"\n  {date_label}"
                    f"{recurrence_label}"
                )

            lines.extend(
                [
                    "",
                    "Please use a more specific title.",
                ]
            )

            await update.message.reply_text(
                "\n".join(lines),
                parse_mode="HTML",
                reply_markup=get_persistent_main_keyboard(),
            )
            return

        event = events[0]

        title = event.get(
            "summary",
            "Untitled Event",
        )

        date_label = get_event_date_label(
            event
        )

        is_recurring = is_recurring_calendar_event(
            event
        )

        delete_calendar_series(
            event
        )

        heading = (
            "🗑️ <b>Recurring Event Series Deleted</b>"
            if is_recurring
            else "🗑️ <b>Calendar Event Deleted</b>"
        )

        message = (
            f"{heading}\n\n"
            f"📌 <b>{escape(title)}</b>\n"
            f"📅 {escape(date_label)}"
        )

        if is_recurring:
            message += (
                "\n🔁 All future occurrences were removed."
            )

        await update.message.reply_text(
            message,
            parse_mode="HTML",
            reply_markup=get_persistent_main_keyboard(),
        )

    except Exception:
        logger.exception(
            "Failed to delete Calendar event."
        )

        await update.message.reply_text(
            (
                "❌ <b>Event Not Deleted</b>\n\n"
                "Something went wrong while updating Google Calendar."
            ),
            parse_mode="HTML",
            reply_markup=get_persistent_main_keyboard(),
        )