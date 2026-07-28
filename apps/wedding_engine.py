"""
ShaunMariaOS

Wedding Engine
"""

from datetime import datetime

from apps.database_engine import (
    get_budget_sheet,
    get_timeline_sheet,
)
from apps.formatting_engine import money
from apps.sheets_engine import clear_worksheet_cache
from constants import BUDGET_SHEET
from services.sheet_writer import update_cells
from utils.sheet_parser import (
    get_budget_summary,
    get_guest_summary,
)
from utils.time import sg_now
from utils.logger import logger


WEDDING_DATE = datetime(2026, 10, 31)


# ====================================================
# Wedding Countdown
# ====================================================

def wedding_days_remaining() -> int:
    """Return the number of days remaining until the wedding."""

    return (
        WEDDING_DATE.date()
        - sg_now().date()
    ).days


# ====================================================
# Wedding Budget Contributions
# ====================================================

def find_current_savings_cell() -> str:
    """
    Locate the value cell beside the Current Savings label.

    Example:
        Current Savings label is in A24.
        Savings value is in B24.

        Returns:
            B24
    """

    rows = get_budget_sheet(
        force_refresh=True,
    )

    for row_index, row in enumerate(
        rows,
        start=1,
    ):
        if not row:
            continue

        label = str(row[0]).strip().lower()

        if label.startswith("current savings"):
            return f"B{row_index}"

    raise RuntimeError(
        "Unable to locate the Current Savings row "
        "in the Wedding Budget sheet."
    )


def add_wedding_contribution(
    amount: float,
) -> dict:
    """
    Add money to the wedding fund.

    The function:
        1. Validates the contribution.
        2. Reads the latest wedding budget.
        3. Finds the Current Savings cell dynamically.
        4. Adds the contribution.
        5. Updates Google Sheets.
        6. Returns the refreshed budget summary.
    """

    if amount <= 0:
        raise ValueError(
            "Wedding contribution must be greater than zero."
        )

    if amount > 10000:
        raise ValueError(
            "Wedding contribution seems unusually high."
        )

    current_budget = get_budget_summary(
        force_refresh=True,
    )

    previous_savings = current_budget[
        "current_savings"
    ]

    updated_savings = (
        previous_savings + amount
    )

    savings_cell = find_current_savings_cell()

    logger.info(
    "Wedding contribution update: cell=%s old=%.2f new=%.2f",
    savings_cell,
    previous_savings,
    updated_savings,
    )

    update_result = update_cells(
        BUDGET_SHEET,
        {
            savings_cell: updated_savings,
        },
    )

    logger.info(
    "Wedding contribution Sheets result: %s",
    update_result,
    )

    if (
        not update_result.get("success")
        or update_result.get("updated_cells", 0) < 1
    ):
        raise RuntimeError(
            "Google Sheets did not confirm the wedding "
            "savings update."
        )

    clear_worksheet_cache(
        BUDGET_SHEET,
    )

    refreshed_budget = get_budget_summary(
        force_refresh=True,
    )

    return {
        "contribution": amount,
        "previous_savings": previous_savings,
        "current_savings": refreshed_budget[
            "current_savings"
        ],
        "balance": refreshed_budget["balance"],
        "shortfall": refreshed_budget["shortfall"],
    }


# ====================================================
# Wedding Dashboard
# ====================================================

def get_wedding_dashboard() -> str:
    """Return the main WeddingOS dashboard."""

    return f"""💍 <b>Shaun & Maria Wedding</b>

📅 <b>Wedding Date</b>
31 October 2026

⏳ <b>Countdown</b>
{wedding_days_remaining()} days to go

Commands:
/weddingbudget - Budget summary
/guestlist - Guestlist summary
/timeline - Wedding day timeline"""


def get_wedding_budget() -> str:
    """Return the latest wedding budget summary."""

    budget = get_budget_summary(
        force_refresh=True,
    )

    return f"""💰 <b>Wedding Budget</b>

💍 <b>Total Budget</b>
{money(budget["total_budget"])}

✅ <b>Paid</b>
{money(budget["paid"])}

📉 <b>Balance</b>
{money(budget["balance"])}

🏦 <b>Current Savings</b>
{money(budget["current_savings"])}

⚠️ <b>Shortfall</b>
{money(budget["shortfall"])}

📊 <b>Source</b>
Live from Google Sheets"""


def get_guestlist_summary() -> str:
    """Return the latest guest-list summary."""

    guest = get_guest_summary()

    return f"""👥 <b>Guestlist Summary</b>

👔 <b>Shaun</b>
{guest["shaun_total"]}

👰 <b>Maria</b>
{guest["maria_total"]}

👥 <b>Total Guests</b>
{guest["total_guests"]}

🪑 <b>Seats Available</b>
{guest["seats_available"]}

💌 <b>Physical Cards</b>
Total: {guest["cards_total"]}
Shaun: {guest["cards_shaun"]}
Maria: {guest["cards_maria"]}
Balance: {guest["cards_balance"]}

📊 <b>Source</b>
Live from Google Sheets"""


def get_wedding_summary() -> dict:
    """Return WeddingOS data for other dashboards."""

    budget = get_budget_summary()
    guest = get_guest_summary()

    return {
        **budget,
        "days_remaining": wedding_days_remaining(),
        "guest_total": guest["total_guests"],
        "seats_available": guest["seats_available"],
    }


# ====================================================
# Wedding Timeline
# ====================================================

def parse_time_to_datetime(
    time_text,
) -> datetime | None:
    """
    Convert a wedding timeline time value into a datetime.
    """

    text = str(time_text).strip().lower()

    if not text:
        return None

    formats = [
        "%I.%M%p",
        "%I:%M%p",
        "%I.%M %p",
        "%I:%M %p",
        "%H:%M",
    ]

    for time_format in formats:
        try:
            parsed_time = datetime.strptime(
                text,
                time_format,
            ).time()

            return datetime.combine(
                WEDDING_DATE.date(),
                parsed_time,
            )

        except ValueError:
            continue

    return None


def build_timeline_events(
    rows: list[list[str]],
) -> list[dict]:
    """Build sorted wedding timeline events from sheet rows."""

    events = []

    for row in rows:
        padded = row + [""] * 7

        timeline_items = [
            (
                padded[0],
                padded[1],
                padded[2],
                "D-Day",
            ),
            (
                padded[4],
                padded[5],
                padded[6],
                "Reception",
            ),
        ]

        for (
            time_text,
            activity,
            poc,
            section,
        ) in timeline_items:

            event_time = parse_time_to_datetime(
                time_text,
            )

            if event_time and activity:
                events.append(
                    {
                        "time": time_text,
                        "datetime": event_time,
                        "activity": activity,
                        "poc": poc,
                        "section": section,
                    }
                )

    return sorted(
        events,
        key=lambda event: event["datetime"],
    )


def format_timeline_event(
    event: dict,
) -> str:
    """Format one wedding timeline event."""

    message = (
        f"{event['time']} - "
        f"{event['activity']}"
    )

    if event["poc"]:
        message += f"\nPOC: {event['poc']}"

    return message


def get_wedding_timeline() -> str:
    """Return the full WeddingOS timeline."""

    events = build_timeline_events(
        get_timeline_sheet()
    )

    if not events:
        return "⚠️ No timeline items found."

    now = sg_now()
    days_remaining = wedding_days_remaining()

    lines = [
        "❤️ <b>Wedding Operations Timeline</b>",
        "",
    ]

    if days_remaining > 0:
        lines.extend(
            [
                "⏳ <b>Wedding Countdown</b>",
                f"{days_remaining} days to go",
                "",
                "⏭️ <b>First Task</b>",
                format_timeline_event(events[0]),
                "",
            ]
        )

    elif days_remaining == 0:
        lines.extend(
            [
                "🟢 <b>Wedding Day Live Mode</b>",
                "",
            ]
        )

        current_event = None
        next_event = None

        for event in events:
            event_datetime = event["datetime"]

            if event_datetime <= now:
                current_event = event

            elif event_datetime > now:
                next_event = event
                break

        if current_event:
            lines.extend(
                [
                    "📍 <b>Current / Latest Task</b>",
                    format_timeline_event(
                        current_event
                    ),
                    "",
                ]
            )

        if next_event:
            lines.extend(
                [
                    "⏭️ <b>Next Task</b>",
                    format_timeline_event(
                        next_event
                    ),
                    "",
                ]
            )

    else:
        lines.extend(
            [
                "📦 <b>Wedding timeline archived.</b>",
                "",
            ]
        )

    lines.append("📋 <b>Full Timeline</b>")

    for event in events:
        poc_text = (
            f" — {event['poc']}"
            if event["poc"]
            else ""
        )

        lines.append(
            f"{event['time']} - "
            f"{event['activity']}"
            f"{poc_text}"
        )

    lines.extend(
        [
            "",
            "📊 <b>Source</b>",
            "Live from Google Sheets",
        ]
    )

    return "\n".join(lines)