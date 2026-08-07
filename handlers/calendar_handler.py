"""
ShaunMariaOS

Calendar Handler
Telegram interface for CalendarOS Core.
"""

from html import escape

from telegram import Update

from apps.menu_keyboard import get_persistent_main_keyboard
from core.calendar_service import create_event_from_text
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
    """Create a Calendar event through CalendarOS Core."""

    if not update.message:
        return

    try:
        result = create_event_from_text(
            text
        )

        if not result.success:
            if result.status == "monthly_day_missing":
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

            await update.message.reply_text(
                (
                    "⚠️ <b>Calendar Event Not Added</b>\n\n"
                    f"{escape(result.message)}\n\n"
                    "Examples:\n"
                    "<code>Dinner with Maria tmrw 7pm</code>\n"
                    "<code>JB trip Saturday to Sunday</code>\n"
                    "<code>Gym every Monday 7pm</code>"
                ),
                parse_mode="HTML",
                reply_markup=get_persistent_main_keyboard(),
            )
            return

        parsed_event = result.parsed_event or {}
        created_event = result.created_event or {}

        title = parsed_event.get(
            "title",
            "Untitled Event",
        )

        recurrence = parsed_event.get(
            "recurrence"
        )

        if parsed_event.get("all_day"):
            start_date = parsed_event[
                "start_date"
            ]

            end_date = parsed_event[
                "end_date"
            ]

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
            "CalendarOS Core request failed."
        )

        await update.message.reply_text(
            (
                "❌ <b>Calendar Event Not Added</b>\n\n"
                "Something went wrong while updating Google Calendar."
            ),
            parse_mode="HTML",
            reply_markup=get_persistent_main_keyboard(),
        )