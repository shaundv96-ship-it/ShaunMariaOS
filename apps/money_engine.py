"""
ShaunMariaOS

Money Engine
Handles all financial calculations.
"""

from apps.database_engine import (
    get_finance_sheet,
    get_expense_log_sheet,
)

# ==========================================
# Finance Sheet Columns
# ==========================================

CATEGORY_COL = 1
ITEM_COL = 2
OWNER_COL = 3
AMOUNT_COL = 4
STATUS_COL = 8

# ==========================================
# Expense Log Columns
# ==========================================

EXPENSE_DATE_COL = 0
EXPENSE_TIME_COL = 1
EXPENSE_OWNER_COL = 2
EXPENSE_CATEGORY_COL = 3
EXPENSE_ITEM_COL = 4
EXPENSE_AMOUNT_COL = 5
EXPENSE_PAYMENT_METHOD_COL = 6
EXPENSE_NOTES_COL = 7
EXPENSE_STATUS_COL = 8


def get_total_income() -> float:
    """
    Return total income received.
    Only rows marked as Paid are counted.
    """

    rows = get_finance_sheet()

    total = 0.0

    for row in rows[1:]:

        if len(row) <= STATUS_COL:
            continue

        category = str(row[CATEGORY_COL]).strip().lower()
        status = str(row[STATUS_COL]).strip().lower()

        if category != "income":
            continue

        if status != "paid":
            continue

        try:
            total += float(row[AMOUNT_COL])
        except (ValueError, TypeError):
            continue

    return total


def get_total_expenses() -> float:
    """
    Return total valid expenses logged.
    """

    rows = get_expense_log_sheet()
    total = 0.0

    for row in rows[1:]:

        if len(row) <= EXPENSE_STATUS_COL:
            continue

        status = str(row[EXPENSE_STATUS_COL]).strip().lower()

        if status not in {"active", "paid", "completed"}:
            continue

        try:
            total += float(row[EXPENSE_AMOUNT_COL])
        except (ValueError, TypeError):
            continue

    return total

def get_monthly_cash_flow() -> float:
    """
    Return income received minus expenses logged.

    This represents monthly cash flow, not the user's
    actual bank-account balance.
    """

    return get_total_income() - get_total_expenses()




def get_allocated_money() -> float:
    """
    Return money that has already been set aside.

    Only non-income Finance rows marked as Allocated
    are counted.
    """

    rows = get_finance_sheet()
    total = 0.0

    for row in rows[1:]:

        if len(row) <= STATUS_COL:
            continue

        category = str(row[CATEGORY_COL]).strip().lower()
        status = str(row[STATUS_COL]).strip().lower()

        if category == "income":
            continue

        if status != "allocated":
            continue

        try:
            total += float(row[AMOUNT_COL])
        except (ValueError, TypeError):
            continue

    return total

def get_available_money() -> float:
    """
    Return this month's currently available money.

    Income received
    minus expenses logged
    minus money already allocated.
    """

    return (
        get_total_income()
        - get_total_expenses()
        - get_allocated_money()
    )

def get_money_summary() -> dict:
    """
    Return the current MoneyOS summary.
    """

    income = get_total_income()
    expenses = get_total_expenses()
    allocated = get_allocated_money()

    monthly_cash_flow = income - expenses
    available_money = monthly_cash_flow - allocated

    return {
        "income": income,
        "expenses": expenses,
        "allocated": allocated,
        "monthly_cash_flow": monthly_cash_flow,
        "available_money": available_money,
    }

if __name__ == "__main__":
    print(get_money_summary())

def get_money_dashboard() -> str:
    """
    Return the main MoneyOS dashboard.
    """

    summary = get_money_summary()

    return f"""
💰 <b>MoneyOS</b>

━━━━━━━━━━━━━━━━━━

💵 <b>Income Received</b>
${summary["income"]:,.2f}

💸 <b>Spent</b>
${summary["expenses"]:,.2f}

🔒 <b>Allocated</b>
${summary["allocated"]:,.2f}

━━━━━━━━━━━━━━━━━━

💳 <b>Available to Spend</b>
${summary["available_money"]:,.2f}

📈 <b>Monthly Cash Flow</b>
${summary["monthly_cash_flow"]:,.2f}
"""