"""
ShaunMariaOS

Salary Engine
"""

from apps.formatting_engine import money, percent
from utils.sheet_parser import get_finance_summary


def get_salary_dashboard():
    finance = get_finance_summary()

    income = finance["salary"]
    savings = finance["savings"]
    bills = finance["bills"]
    insurance = finance["insurance"]
    commitments = finance["commitments"]
    available = finance["available"]
    health = finance["health"]

    savings_rate = (savings / income * 100) if income else 0
    commitment_rate = (commitments / income * 100) if income else 0
    available_rate = (available / income * 100) if income else 0

    return f"""💵 <b>Salary Dashboard</b>

━━━━━━━━━━━━━━━━━━

💰 <b>Monthly Salary</b>
{money(income)}

━━━━━━━━━━━━━━━━━━

📊 <b>Monthly Commitments</b>

🏦 Savings
{money(savings)}

🧾 Bills
{money(bills)}

🛡 Insurance
{money(insurance)}

📋 Total Commitments
{money(commitments)}

━━━━━━━━━━━━━━━━━━

💳 <b>Available Cash</b>
{money(available)}

{health}

━━━━━━━━━━━━━━━━━━

📈 <b>Allocation</b>

Savings
{percent(savings_rate)}

Commitments
{percent(commitment_rate)}

Available
{percent(available_rate)}

━━━━━━━━━━━━━━━━━━

🧠 <b>Insight</b>

Your recurring commitments total {money(commitments)} each month.

You currently retain approximately {percent(available_rate)} of your income after planned savings and recurring expenses.
"""