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
    print(summary)

    message = "💸 <b>Expense Summary</b>\n\n"
    message += "📅 <b>This Month</b>\n\n"

    message += (
        f"🧾 <b>Transactions</b>\n"
        f"{summary['count']}\n\n"
    )

    message += (
        f"💰 <b>Total Spent</b>\n"
        f"{money(summary['total'])}\n\n"
    )

    message += "━━━━━━━━━━━━━━━━━━\n\n"
    message += "📊 <b>Categories</b>\n"

    if not summary["categories"]:
        message += "\nNo expenses recorded."
        return message

    for category, total in sorted(
        summary["categories"].items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        icon = CATEGORY_ICONS.get(category, "📦")

        message += (
            f"\n{icon} <b>{category}</b>\n"
            f"{money(total)}\n"
        )

    highest_category = summary.get("highest_category", "")
    highest_category_total = summary.get(
        "highest_category_total",
        0,
    )
    average = summary.get("average", 0)
    largest_expense = summary.get(
        "largest_expense",
        {
            "item": "",
            "amount": 0,
        },
    )

    message += "\n━━━━━━━━━━━━━━━━━━\n\n"
    message += "🧠 <b>Insights</b>\n"

    if highest_category:
        highest_icon = CATEGORY_ICONS.get(
            highest_category,
            "📦",
        )

        message += (
            f"\n🥇 <b>Highest Category</b>\n"
            f"{highest_icon} {highest_category}\n"
            f"{money(highest_category_total)}\n"
        )

    message += (
        f"\n💵 <b>Average Transaction</b>\n"
        f"{money(average)}\n"
    )

    if largest_expense.get("item"):
        message += (
            f"\n🔥 <b>Largest Expense</b>\n"
            f"{largest_expense['item']}\n"
            f"{money(largest_expense['amount'])}\n"
        )

    return message