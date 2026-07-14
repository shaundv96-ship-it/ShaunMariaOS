"""
ShaunMariaOS

Expense Summary Engine
"""

from datetime import datetime

from apps.formatting_engine import money
from utils.category_icons import CATEGORY_ICONS
from utils.sheet_parser import get_expense_summary


def get_expense_dashboard():
    """Build the monthly expense dashboard."""

    summary = get_expense_summary()
    month_title = datetime.now().strftime("%B %Y")

    sections = [
        "💸 <b>Expense Summary</b>\n",
        f"📅 <b>{month_title}</b>",
        (
            f"\n\n🧾 <b>Transactions</b>\n"
            f"{summary['count']}"
        ),
        (
            f"\n\n💰 <b>Total This Month</b>\n"
            f"{money(summary['total'])}"
        ),
        "\n\n━━━━━━━━━━━━━━━━━━",
        "\n\n📊 <b>Categories</b>",
    ]

    if not summary["categories"]:
        sections.append("\n\nNo expenses recorded.")
        return "".join(sections)

    for category, total in sorted(
        summary["categories"].items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        icon = CATEGORY_ICONS.get(category, "📦")

        sections.append(
            f"\n\n{icon} <b>{category}</b> — {money(total)}"
        )

    sections.extend(
        [
            "\n\n━━━━━━━━━━━━━━━━━━",
            "\n\n🧠 <b>Insights</b>",
        ]
    )

    highest_category = summary.get(
        "highest_category",
        "",
    )

    highest_category_total = summary.get(
        "highest_category_total",
        0,
    )

    if highest_category:
        highest_icon = CATEGORY_ICONS.get(
            highest_category,
            "📦",
        )

        sections.extend(
            [
                "\n\n🥇 <b>Highest Category</b>",
                f"\n\n{highest_icon} {highest_category}",
                f"\n{money(highest_category_total)}",
            ]
        )

    sections.extend(
        [
            "\n\n💵 <b>Average Transaction</b>",
            f"\n\n{money(summary.get('average', 0))}",
        ]
    )

    largest_expense = summary.get(
        "largest_expense",
        {
            "item": "",
            "amount": 0,
        },
    )

    if largest_expense.get("item"):
        sections.extend(
            [
                "\n\n🔥 <b>Largest Expense</b>",
                f"\n\n{largest_expense['item']}",
                f"\n{money(largest_expense['amount'])}",
            ]
        )

    if summary["total"] > 0 and highest_category:
        percentage = (
            highest_category_total
            / summary["total"]
            * 100
        )

        sections.extend(
            [
                "\n\n━━━━━━━━━━━━━━━━━━",
                "\n\n💡 <b>Finance Tip</b>",
                (
                    f"\n\n{highest_category} accounts for "
                    f"{percentage:.0f}% of your spending this month."
                ),
            ]
        )

    return "".join(sections)