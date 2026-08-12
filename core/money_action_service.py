"""
ShaunMariaOS

Money Action Service
Natural-language MoneyOS write actions.
"""

from dataclasses import dataclass
import re

from apps.expense_engine import (
    ExpenseEntry,
    detect_category,
    save_expense,
)
from apps.income_engine import (
    IncomeEntry,
    parse_income,
    save_income,
)


@dataclass
class MoneyActionResult:
    """Structured result for MoneyOS write actions."""

    success: bool
    status: str
    message: str
    data: dict | None = None


def record_expense_from_text(
    text: str,
) -> MoneyActionResult:
    """Parse and save a natural-language expense."""

    text = text.strip()

    amount_match = re.search(
        r"(?:\$\s*|sgd\s*)?"
        r"(\d+(?:,\d{3})*(?:\.\d{1,2})?)",
        text,
        re.IGNORECASE,
    )

    if not amount_match:
        return MoneyActionResult(
            success=False,
            status="invalid",
            message="I couldn't find the expense amount.",
        )

    amount = float(
        amount_match.group(1).replace(",", "")
    )

    if amount <= 0:
        return MoneyActionResult(
            success=False,
            status="invalid",
            message="Expense amount must be greater than zero.",
        )

    item = re.sub(
        r"(?i)\b(?:spent|paid|bought)\b",
        "",
        text,
        count=1,
    )

    item = re.sub(
        r"(?:\$\s*|sgd\s*)?"
        r"\d+(?:,\d{3})*(?:\.\d{1,2})?",
        "",
        item,
        count=1,
        flags=re.IGNORECASE,
    )

    item = re.sub(
        r"(?i)\b(?:on|for)\b",
        "",
        item,
        count=1,
    )

    item = " ".join(
        item.split()
    ).strip()

    if not item:
        item = "Expense"

    item = item[0].upper() + item[1:]

    entry = ExpenseEntry(
        amount=amount,
        item=item,
        category=detect_category(item),
    )

    try:
        save_expense(entry)

        return MoneyActionResult(
            success=True,
            status="created",
            message="Expense recorded.",
            data={
                "amount": entry.amount,
                "item": entry.item,
                "category": entry.category,
                "owner": entry.owner,
            },
        )

    except Exception as exc:
        return MoneyActionResult(
            success=False,
            status="error",
            message=str(exc),
        )


def record_income_from_text(
    text: str,
) -> MoneyActionResult:
    """
    Parse and save supported income.

    Salary entries must identify Shaun or Maria.
    """

    parsed = parse_income(text)

    if parsed is None:
        return MoneyActionResult(
            success=False,
            status="invalid",
            message="I couldn't find the income amount.",
        )

    lowered = text.casefold()

    if "salary" not in lowered:
        return MoneyActionResult(
            success=False,
            status="unsupported",
            message=(
                "That income type isn't mapped yet. "
                "Try: Shaun Salary 3013.80 "
                "or Maria Salary 1800."
            ),
        )

    if not parsed.owner:
        return MoneyActionResult(
            success=False,
            status="owner_required",
            message=(
                "Whose salary is this? "
                "Try: Shaun Salary 3013.80 "
                "or Maria Salary 1800."
            ),
        )

    if not parsed.item:
        return MoneyActionResult(
            success=False,
            status="invalid",
            message="I couldn't identify the salary row.",
        )

    try:
        result = save_income(parsed)

        return MoneyActionResult(
            success=True,
            status="updated",
            message="Income updated.",
            data=result,
        )

    except Exception as exc:
        return MoneyActionResult(
            success=False,
            status="error",
            message=str(exc),
        )