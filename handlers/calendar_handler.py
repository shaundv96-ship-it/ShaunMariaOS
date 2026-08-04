"""
ShaunMariaOS

Calendar Handler
"""

from html import escape

from telegram import Update

from apps.calendar_engine import create_calendar_event
from apps.calendar_parser import parse_calendar_event
from apps.menu_keyboard import get_persistent_main_keyboard
from utils.logger import logger


def format_time_12h(value) -> str:
    """Format a datetime as 12-hour time without a leading zero."""

    return value.strftime("%I:%M %p").lstrip("0")


def format_all_day_dates(
    start_date,
    end_date,
) -> str:
    """Return a readable inclusive all-day date range."""

    if start_date == end_date:
        return start_date.strftime(
            "%A, %d %B %Y"
        )

    if (
        start_date.month == end_date.month
        and start_date.year == end_date.year
    ):
        return (
            f"{start_date.strftime('%d')}"
            f"–{end_date.strftime('%d %B %Y')}"
        )

    if start_date.year == end_date.year:
        return (
            f"{start_date.strftime('%d %B')}"
            f" – "
            f"{end_date.strftime('%d %B %Y')}"
        )

    return (
        f"{start_date.strftime('%d %B %Y')}"
        f" – "
        f"{end_date.strftime('%d %B %Y')}"
    )


async def handle_calendar(
    update: Update,
    text: str,
) -> None:
    """Parse and create a natural-language calendar event."""

    if not update.message:
        return

    parsed_event = parse_calendar_event(
        text
    )
    if (
    parsed_event
    and parsed_event.get("incomplete")
):
        await update.message.reply_text(
        (
            "📅 <b>Monthly Event Needs a Day</b>\n\n"
            "Which day should it repeat each month?\n\n"
            "Examples:\n"
            "<code>Pay insurance every month on the 1st</code>\n"
            "<code>Pay SIM bill every month on the 21st</code>"
        ),
        parse_mode="HTML",
        reply_markup=get_persistent_main_keyboard(),
    )
    return

    if parsed_event is None:
        await update.message.reply_text(
            (
                "⚠️ <b>Calendar Event Not Added</b>\n\n"
                "Please include a date, or a date and time.\n\n"
                "Examples:\n"
                "<code>Dinner with Maria tmrw 7pm</code>\n"
                "<code>JB trip Saturday to Sunday</code>\n"
                "<code>Gym every Monday 7pm</code>"
            ),
            parse_mode="HTML",
            reply_markup=get_persistent_main_keyboard(),
        )
        return

    try:
        title = parsed_event["title"]
        all_day = parsed_event["all_day"]
        recurrence = parsed_event.get(
            "recurrence"
        )

        if all_day:
            start_date = parsed_event[
                "start_date"
            ]

            end_date = parsed_event[
                "end_date"
            ]

            created_event = create_calendar_event(
                title=title,
                start_date=start_date,
                end_date=end_date,
                all_day=True,
                recurrence=recurrence,
            )

            event_details = (
                "📅 "
                f"{escape(format_all_day_dates(start_date, end_date))}\n"
                "🌍 All day"
            )

        else:
            start_time = parsed_event[
                "start_time"
            ]

            end_time = parsed_event[
                "end_time"
            ]

            created_event = create_calendar_event(
                title=title,
                start_time=start_time,
                end_time=end_time,
                all_day=False,
                recurrence=recurrence,
            )

            date_label = start_time.strftime(
                "%A, %d %B %Y"
            )

            time_label = (
                f"{format_time_12h(start_time)}"
                f" – "
                f"{format_time_12h(end_time)}"
            )

            event_details = (
                f"📅 {escape(date_label)}\n"
                f"🕒 {escape(time_label)}"
            )

        heading = (
            "🔁 <b>Recurring Event Added</b>"
            if recurrence
            else "✅ <b>Calendar Event Added</b>"
        )

        message = (
            f"{heading}\n\n"
            f"📌 <b>{escape(title)}</b>\n\n"
            f"{event_details}"
        )

        if recurrence:
            message += (
                "\n"
                f"🔁 {escape(recurrence['label'])}"
            )

        calendar_link = created_event.get(
            "htmlLink"
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
            "Failed to create calendar event."
        )

        await update.message.reply_text(
            (
                "❌ <b>Calendar Event Not Added</b>\n\n"
                "Something went wrong while updating Google Calendar."
            ),
            parse_mode="HTML",
            reply_markup=get_persistent_main_keyboard(),
        )