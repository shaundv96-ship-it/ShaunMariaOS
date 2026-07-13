"""
ShaunMariaOS

Expense Summary Engine
"""

from utils.sheet_parser import get_expense_summary
from apps.formatting_engine import money
from utils.category_icons import CATEGORY_ICONS


def get_expense_dashboard():

    summary = get_expense_summary()

    message = "💸 <b>Expense Summary</b>\n\n"

    message += f"📅 <b>This Month</b>\n\n"

    message += f"Transactions\n{summary['count']}\n\n"

    message += f"Total Spent\n{money(summary['total'])}\n\n"

    message += "━━━━━━━━━━━━━━━━━━\n\n"

    message += "<b>Categories</b>\n"

    if not summary["categories"]:

        message += "\nNo expenses recorded."

    else:

        for category, total in sorted(
        summary["categories"].items()
        ):

        icon = CATEGORY_ICONS.get(category, "📦")

     message += (
        f"\n{icon} {category}\n"
        f"{money(total)}\n"
        )

    return message