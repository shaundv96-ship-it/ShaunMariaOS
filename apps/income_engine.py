"""
ShaunMariaOS

Income Engine
"""

from dataclasses import dataclass
from datetime import datetime
import re

from apps.database_engine import get_finance_sheet
from services.sheet_writer import update_cells


FINANCE_SHEET_NAME = "Finance"


@dataclass
class IncomeEntry:
    amount: float
    owner: str
    item: str


def parse_income(text: str) -> IncomeEntry | None:
    """
    Parse a salary or income message.

    Example:
        Salary $3600
    """

    text = text.strip()

    amount_match = re.search(
        r"\$?\s*(\d+(?:,\d{3})*(?:\.\d{1,2})?)",
        text,
    )

    if not amount_match:
        return None

    amount_text = amount_match.group(1).replace(",", "")
    amount = float(amount_text)

    return IncomeEntry(
    amount=amount,
    owner="",
    item="",
    )


def save_income(entry: IncomeEntry) -> dict:
    """
    Update the matching income row in the Finances sheet.
    """

    rows = get_finance_sheet()

    target_row = None

    for row_number, row in enumerate(
        rows,
        start=1,
    ):
        if len(row) < 4:
            continue

        category = str(row[1]).strip().lower()
        item = str(row[2]).strip().lower()
        owner = str(row[3]).strip().lower()

        if (
            category == "income"
            and item == entry.item.lower()
            and owner == entry.owner.lower()
        ):
            target_row = row_number
            break

    if target_row is None:
        raise ValueError(
            f"Income row not found for {entry.owner}."
        )

    last_updated = datetime.now().strftime(
        "%d %B %Y"
    )

    return update_cells(
        FINANCE_SHEET_NAME,
        {
            f"E{target_row}": entry.amount,
            f"J{target_row}": last_updated,
        },
    )