"""
ShaunMariaOS

Income Engine
"""

from dataclasses import dataclass
import re

from apps.database_engine import (
    FINANCE_SHEET,
    get_finance_sheet,
)
from apps.sheets_engine import clear_worksheet_cache
from services.sheet_writer import update_cells
from apps.money_engine import get_money_summary
from utils.time import sg_now


@dataclass
class IncomeEntry:
    amount: float
    owner: str = ""
    item: str = ""


def parse_income(
    text: str,
) -> IncomeEntry | None:
    """
    Parse a salary or income message.

    Examples:
        Salary 3013.80
        Salary $3,013.80
        Bonus SGD 500
    """

    amount_match = re.search(
        r"(?:\$\s*|sgd\s*)?"
        r"(\d+(?:,\d{3})*(?:\.\d{1,2})?)",
        text.strip(),
        re.IGNORECASE,
    )

    if not amount_match:
        return None

    amount = float(
        amount_match.group(1).replace(",", "")
    )

    if amount <= 0:
        return None

    return IncomeEntry(
        amount=amount,
    )


def find_income_row(
    entry: IncomeEntry,
) -> int:
    """Return the matching Finance-sheet row number."""

    rows = get_finance_sheet(
        force_refresh=True,
    )

    expected_item = entry.item.strip().casefold()
    expected_owner = entry.owner.strip().casefold()

    for row_number, row in enumerate(
        rows,
        start=1,
    ):
        if len(row) < 4:
            continue

        category = str(row[1]).strip().casefold()
        item = str(row[2]).strip().casefold()
        owner = str(row[3]).strip().casefold()

        if (
            category == "income"
            and item == expected_item
            and owner == expected_owner
        ):
            return row_number

    raise ValueError(
        f"Income row not found for {entry.owner}."
    )


def validate_income_entry(
    entry: IncomeEntry,
) -> None:
    """Validate an income entry before writing to Google Sheets."""

    if entry.amount <= 0:
        raise ValueError(
            "Income must be greater than zero."
        )

    if not entry.owner.strip():
        raise ValueError(
            "Income owner is missing."
        )

    if not entry.item.strip():
        raise ValueError(
            "Income item is missing."
        )


def save_income(
    entry: IncomeEntry,
) -> dict:
    """
    Update the matching income row.

    Recording income also marks its status as Paid,
    clears the Finance-sheet cache, and returns the
    refreshed MoneyOS summary.
    """

    validate_income_entry(entry)

    target_row = find_income_row(entry)

    last_updated = sg_now().strftime(
        "%d %B %Y"
    )

    update_result = update_cells(
        FINANCE_SHEET,
        {
            f"E{target_row}": entry.amount,
            f"I{target_row}": "Paid",
            f"J{target_row}": last_updated,
        },
    )

    if (
        not update_result.get("success")
        or update_result.get("updated_cells", 0) < 1
    ):
        raise RuntimeError(
            "Google Sheets did not confirm the income update."
        )

    clear_worksheet_cache(
        FINANCE_SHEET,
    )

    money_summary = get_money_summary(
        force_refresh=True,
    )

    return {
        "amount": entry.amount,
        "owner": entry.owner,
        "item": entry.item,
        "finance": money_summary,
        "updated_cells": update_result.get(
            "updated_cells",
            0,
        ),
    }