"""
ShaunMariaOS

Calendar Update Handler
"""

from datetime import date, datetime, timedelta
from html import escape

from telegram import Update

from apps.calendar_engine import (
    get_event_date_label,
    search_upcoming_calendar_events,
    update_calendar_event,
)
from apps.calendar_update_parser import (
    parse_calendar_update,
)
from apps.menu_keyboard import (
    get_persistent_main_keyboard,
)
from utils.logger import logger
from utils.time import SINGAPORE_TZ


def parse_google_datetime(
    value: str,
) -> datetime:
    """Parse a Google Calendar datetime."""

    return datetime.fromisoformat(
        value.replace(
            "Z",
            "+00:00",
        )
    ).astimezone(
        SINGAPORE_TZ
    )


def build_timed_update(
    event: dict,
    parsed_update: dict,
) -> dict:
    """Build start/end changes for a timed event."""

    start_text = event["start"]["dateTime"]
    end_text = event["end"]["dateTime"]

    current_start = parse_google_datetime(
        start_text
    )

    current_end = parse_google_datetime(
        end_text
    )

    duration = (
        current_end
        - current_start
    )

    requested_date = (
        parsed_update.get("new_date")
        or current_start.date()
    )

    requested_time = (
        parsed_update.get("new_time")
        or current_start.time()
    )

    new_start = datetime.combine(
        requested_date,
        requested_time,
        tzinfo=SINGAPORE_TZ,
    )

    new_end = (
        new_start
        + duration
    )

    return {
        "start": {
            "dateTime": new_start.isoformat(),
            "timeZone": "Asia/Singapore",
        },
        "end": {
            "dateTime": new_end.isoformat(),
            "timeZone": "Asia/Singapore",
        },
    }


def build_all_day_update(
    event: dict,
    parsed_update: dict,
) -> dict:
    """
    Build date changes for an all-day event.

    Google Calendar stores all-day end dates exclusively.
    """

    current_start = date.fromisoformat(
        event["start"]["date"]
    )

    current_exclusive_end = date.fromisoformat(
        event["end"]["date"]
    )

    current_inclusive_end = (
        current_exclusive_end
        - timedelta(days=1)
    )

    current_span = (
        current_inclusive_end
        - current_start
    )

    requested_start = parsed_update.get(
        "new_start_date"
    )

    requested_end = parsed_update.get(
        "new_end_date"
    )

    if requested_start and requested_end:
        new_start = requested_start
        new_inclusive_end = requested_end

    else:
        new_start = (
            parsed_update.get("new_date")
            or current_start
        )

        new_inclusive_end = (
            new_start
            + current_span
        )

    return {
        "start": {
            "date": new_start.isoformat(),
        },
        "end": {
            "date": (
                new_inclusive_end
                + timedelta(days=1)
            ).isoformat(),
        },
    }


def build_updated_date_label(
    event: dict,
) -> str:
    """Return the updated event's date label."""

    return get_event_date_label(
        event
    )


async def handle_calendar_update(
    update: Update,
    text: str,
) -> None:
    """Find and update one Calendar event safely."""

    if not update.message:
        return

    parsed_update = parse_calendar_update(
        text
    )

    if parsed_update is None:
        await update.message.reply_text(
            (
                "⚠️ <b>Calendar Event Not Updated</b>\n\n"
                "Try:\n"
                "<code>Move dinner to Friday 8pm</code>\n"
                "<code>Change meeting to 3pm</code>\n"
                "<code>Rename dinner to Anniversary Dinner</code>"
            ),
            parse_mode="HTML",
            reply_markup=get_persistent_main_keyboard(),
        )
        return

    try:
        search_text = parsed_update[
            "search_text"
        ]

        events = search_upcoming_calendar_events(
            search_text
        )

        if not events:
            await update.message.reply_text(
                (
                    "🔎 <b>Event Not Found</b>\n\n"
                    f"I couldn't find an upcoming event matching "
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
                "Nothing was changed. I found:",
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

                lines.append(
                    f"\n• <b>{title}</b>"
                    f"\n  {date_label}"
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
        event_id = event["id"]

        updates = {}

        if parsed_update["action"] == "rename":
            updates["summary"] = parsed_update[
                "new_title"
            ]

        else:
            is_all_day = (
                "date"
                in event.get(
                    "start",
                    {},
                )
            )

            if is_all_day:
                if parsed_update.get(
                    "new_time"
                ):
                    await update.message.reply_text(
                        (
                            "⚠️ <b>Event Not Updated</b>\n\n"
                            "This is currently an all-day event. "
                            "Changing it to a timed event will be "
                            "added in a later update."
                        ),
                        parse_mode="HTML",
                        reply_markup=get_persistent_main_keyboard(),
                    )
                    return

                updates.update(
                    build_all_day_update(
                        event,
                        parsed_update,
                    )
                )

            else:
                if parsed_update.get(
                    "new_start_date"
                ):
                    await update.message.reply_text(
                        (
                            "⚠️ <b>Event Not Updated</b>\n\n"
                            "A multi-day range cannot currently "
                            "be applied to a timed event."
                        ),
                        parse_mode="HTML",
                        reply_markup=get_persistent_main_keyboard(),
                    )
                    return

                updates.update(
                    build_timed_update(
                        event,
                        parsed_update,
                    )
                )

        updated_event = update_calendar_event(
            event_id,
            updates,
        )

        updated_title = updated_event.get(
            "summary",
            "Untitled Event",
        )

        updated_date = build_updated_date_label(
            updated_event
        )

        calendar_link = updated_event.get(
            "htmlLink"
        )

        message = (
            "✏️ <b>Calendar Event Updated</b>\n\n"
            f"📌 <b>{escape(updated_title)}</b>\n"
            f"📅 {escape(updated_date)}"
        )

        if calendar_link:
            message += (
                "\n\n"
                f'<a href="{escape(calendar_link, quote=True)}">'
                "🔗 Open in Google Calendar"
                "</a>"
            )

        await update.message.reply_text(
            message,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=get_persistent_main_keyboard(),
        )

    except Exception:
        logger.exception(
            "Failed to update Calendar event."
        )

        await update.message.reply_text(
            (
                "❌ <b>Calendar Event Not Updated</b>\n\n"
                "Something went wrong while updating Google Calendar."
            ),
            parse_mode="HTML",
            reply_markup=get_persistent_main_keyboard(),
        )