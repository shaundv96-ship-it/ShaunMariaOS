"""
ShaunMariaOS

Expense Summary Engine
"""

from apps.formatting_engine import money
from utils.category_icons import CATEGORY_ICONS
from utils.sheet_parser import get_expense_summary


def get_expense_dashboard():
    """Build the monthly expense dashboard."""

    summary = get_expense_summary()

    message = "💸 <b>Expense Summary</b>\n\n"

    message += "📅 <b>This Month</b>\n\n"

    message += (
        f"🧾 Transactions\n"
        f"{summary['count']}\n\n"
    )

    message += (
        f"💰 Total Spent\n"
        f"{money(summary['total'])}\n\n"
    )

    message += "━━━━━━━━━━━━━━━━━━\n\n"

    message += "📊 <b>Categories</b>\n"

    if not summary["categories"]:

        message += "\nNo expenses recorded."

    else:

        for category, total in sorted(
            summary["categories"].items()
        ):

            icon = CATEGORY_ICONS.get(
                category,
                "📦",
            )

            message += (
                f"\n{icon} {category}\n"
                f"{money(total)}\n"
            )

    return message