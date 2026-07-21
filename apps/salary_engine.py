"""
ShaunMariaOS

Salary Engine
"""

from apps.formatting_engine import money, percent
from apps.money_engine import get_money_summary


def get_salary_health(finance: dict) -> str:
    """Return a salary health message."""

    income = finance.get("income", 0.0)
    available = finance.get("available_money", 0.0)

    if income <= 0:
        return "⚪ No salary has been recorded this month."

    if available < 0:
        return "🔴 You have exceeded your available income."

    if available < income * 0.2:
        return "🟠 Less than 20% of your salary remains."

    return "🟢 Your salary is currently on track."


def get_salary_dashboard():
    """Build the Salary Dashboard using MoneyOS."""

    finance = get_money_summary()

    income = finance.get("income", 0.0)
    expenses = finance.get("expenses", 0.0)
    allocated = finance.get("allocated", 0.0)
    available = finance.get("available_money", 0.0)

    allocation_rate = (allocated / income * 100) if income else 0
    spending_rate = (expenses / income * 100) if income else 0
    available_rate = (available / income * 100) if income else 0

    return f"""💼 <b>Salary Dashboard</b>

────────────────────

💵 <b>Income Received</b>
{money(income)}

────────────────────

📌 <b>Budget Overview</b>

📌 Allocated
{money(allocated)}

💸 Spent
{money(expenses)}

💳 Remaining
{money(available)}

────────────────────

📊 <b>Allocation Rates</b>

Allocated
{percent(allocation_rate)}

Spent
{percent(spending_rate)}

Remaining
{percent(available_rate)}

────────────────────

❤️ <b>Status</b>

{get_salary_health(finance)}

────────────────────

🧠 <b>Insight</b>

You have spent {money(expenses)} this month.

You currently have {money(available)} available to spend.
"""