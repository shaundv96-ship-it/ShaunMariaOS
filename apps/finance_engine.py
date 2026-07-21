"""
ShaunMariaOS

Finance Engine
"""

from apps.money_engine import get_money_summary
from apps.formatting_engine import money


def get_finance_health(finance: dict) -> str:
    """Return a simple financial health message."""

    income = finance.get("income", 0.0)
    expenses = finance.get("expenses", 0.0)
    allocated = finance.get("allocated", 0.0)
    available = finance.get("available_money", 0.0)

    if income <= 0 and expenses <= 0 and allocated <= 0:
        return "⚪ No financial activity recorded yet."

    if available < 0:
        return "🔴 Spending and allocations exceed received income."

    if expenses > income:
        return "🔴 Expenses exceed received income."

    if available == 0:
        return "🟠 All received income has been used or allocated."

    return "🟢 Finances are currently within available income."


def get_finance_dashboard():
    """Build the Finance Dashboard using MoneyOS."""

    finance = get_money_summary()
    health = get_finance_health(finance)

    return f"""💰 <b>Finance Dashboard</b>

💵 <b>Income Received</b>
{money(finance.get("income", 0.0))}

💸 <b>Total Expenses</b>
{money(finance.get("expenses", 0.0))}

📌 <b>Allocated</b>
{money(finance.get("allocated", 0.0))}

💳 <b>Available to Spend</b>
{money(finance.get("available_money", 0.0))}

📊 <b>Monthly Cash Flow</b>
{money(finance.get("monthly_cash_flow", 0.0))}

❤️ <b>Financial Health</b>
{health}

📈 <b>Source</b>
MoneyOS (Live from Google Sheets)
"""