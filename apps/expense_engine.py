"""
ShaunMariaOS

Expense Engine
"""

from dataclasses import dataclass

from apps.formatting_engine import money
from services.sheet_writer import append_row
from utils.time import sg_now


EXPENSE_SHEET = "Expense Log"
DEFAULT_OWNER = "Shaun"
DEFAULT_PAYMENT_METHOD = "Not specified"


@dataclass
class ExpenseEntry:
    amount: float
    item: str
    category: str
    owner: str = DEFAULT_OWNER
    payment_method: str = DEFAULT_PAYMENT_METHOD
    notes: str = ""
    status: str = "Active"


def parse_expense_command(arguments: list[str]) -> ExpenseEntry:
    """
    Parse:
    /expense 18.50 Lunch Food

    Format:
    amount item category
    """
    if len(arguments) < 3:
        raise ValueError(
            "Use: /expense <amount> <item> <category>\n"
            "Example: /expense 18.50 Lunch Food"
        )

    try:
        amount = float(
            arguments[0]
            .replace("$", "")
            .replace(",", "")
            .strip()
        )
    except ValueError as error:
        raise ValueError(
            "The expense amount must be a valid number."
        ) from error

    if amount <= 0:
        raise ValueError(
            "The expense amount must be greater than zero."
        )

    item = arguments[1].strip()
    category = " ".join(arguments[2:]).strip()

    if not item:
        raise ValueError("The expense item cannot be empty.")

    if not category:
        raise ValueError("The expense category cannot be empty.")

    return ExpenseEntry(
        amount=amount,
        item=item,
        category=category,
    )


def save_expense(expense: ExpenseEntry) -> dict:
    """Write an expense into the Expense Log worksheet."""
    now = sg_now()

    values = [
        now.strftime("%d %B %Y"),
        now.strftime("%I:%M %p").lstrip("0"),
        expense.owner,
        expense.category,
        expense.item,
        expense.amount,
        expense.payment_method,
        expense.notes,
        expense.status,
    ]

    return append_row(
        EXPENSE_SHEET,
        values,
    )


def format_expense_confirmation(expense: ExpenseEntry) -> str:
    """Return a Telegram confirmation message."""
    return f"""✅ <b>Expense Added</b>

🧾 <b>Item</b>
{expense.item}

🏷 <b>Category</b>
{expense.category}

💰 <b>Amount</b>
{money(expense.amount)}

👤 <b>Owner</b>
{expense.owner}

📊 Google Sheets updated"""