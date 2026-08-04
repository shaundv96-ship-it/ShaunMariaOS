"""
ShaunMariaOS

Money Engine
Handles all MoneyOS calculations.
"""

from utils.sheet_parser import (
    get_expense_summary,
    get_finance_summary,
)


# ==========================================================
# Money Summary
# ==========================================================

def get_money_summary(
    *,
    force_refresh: bool = False,
) -> dict:
    """
    Return the current MoneyOS summary.

    Calculations:
        Monthly cash flow:
            Income received - expenses logged

        Available money:
            Income received
            - expenses logged
            - allocated commitments
    """

    finance = get_finance_summary(
        force_refresh=force_refresh,
    )

    expenses = get_expense_summary()

    income = float(
        finance.get("income", 0.0)
    )

    expense_total = float(
        expenses.get("total", 0.0)
    )

    allocated = float(
        finance.get("commitments", 0.0)
    )

    monthly_cash_flow = (
        income
        - expense_total
    )

    available_money = (
        monthly_cash_flow
        - allocated
    )

    return {
        "income": income,
        "expenses": expense_total,
        "allocated": allocated,
        "monthly_cash_flow": monthly_cash_flow,
        "available_money": available_money,

        # Useful breakdowns for other modules
        "savings": float(
            finance.get("savings", 0.0)
        ),
        "bills": float(
            finance.get("bills", 0.0)
        ),
        "insurance": float(
            finance.get("insurance", 0.0)
        ),
        "health": finance.get(
            "health",
            "",
        ),
    }


# ==========================================================
# Individual Values
# ==========================================================

def get_total_income(
    *,
    force_refresh: bool = False,
) -> float:
    """Return all income marked as received."""

    return get_money_summary(
        force_refresh=force_refresh,
    )["income"]


def get_total_expenses() -> float:
    """Return this month's recorded expenses."""

    return get_money_summary()["expenses"]


def get_allocated_money(
    *,
    force_refresh: bool = False,
) -> float:
    """Return money committed to savings, bills and insurance."""

    return get_money_summary(
        force_refresh=force_refresh,
    )["allocated"]


def get_monthly_cash_flow(
    *,
    force_refresh: bool = False,
) -> float:
    """Return income received minus recorded expenses."""

    return get_money_summary(
        force_refresh=force_refresh,
    )["monthly_cash_flow"]


def get_available_money(
    *,
    force_refresh: bool = False,
) -> float:
    """
    Return income minus expenses and allocated commitments.
    """

    return get_money_summary(
        force_refresh=force_refresh,
    )["available_money"]


# ==========================================================
# Money Dashboard
# ==========================================================

def get_money_dashboard() -> str:
    """Return the main MoneyOS dashboard."""

    summary = get_money_summary(
        force_refresh=True,
    )

    return f"""💰 <b>MoneyOS</b>

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

━━━━━━━━━━━━━━━━━━

🏦 <b>Allocation Breakdown</b>

Savings: ${summary["savings"]:,.2f}
Bills: ${summary["bills"]:,.2f}
Insurance: ${summary["insurance"]:,.2f}
"""


# ==========================================================
# Local Test
# ==========================================================

if __name__ == "__main__":
    from pprint import pprint

    pprint(
        get_money_summary(
            force_refresh=True,
        )
    )