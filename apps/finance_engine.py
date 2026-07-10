"""
ShaunMariaOS

Finance Engine
"""

from utils.sheet_parser import get_finance_summary


def money(value):
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


def get_finance_dashboard():
    finance = get_finance_summary()

    return f"""💰 <b>Finance Dashboard</b>

💵 <b>Income</b>
{money(finance["salary"])}

🏦 <b>Savings</b>
{money(finance["savings"])}

🧾 <b>Bills</b>
{money(finance["bills"])}

🛡 <b>Insurance</b>
{money(finance["insurance"])}

📋 <b>Total Commitments</b>
{money(finance["commitments"])}

💳 <b>Available Cash</b>
{money(finance["available"])}

📊 <b>Cash Flow</b>
{finance["health"]}

📈 <b>Source</b>
Live from Google Sheets"""