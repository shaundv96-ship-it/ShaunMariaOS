"""
ShaunMariaOS

Salary Engine
"""

from apps.database_engine import get_finance_sheet


def money(value):
    try:
        amount = float(str(value).replace("$", "").replace(",", ""))
        return f"${amount:,.2f}"
    except:
        return str(value)


def get_salary_dashboard():

    rows = get_finance_sheet()

    income = 0
    savings = 0
    bills = 0
    insurance = 0

    for row in rows:

        if len(row) < 9:
            continue

        category = str(row[1]).strip()
        amount = row[4]
        status = str(row[8]).strip()

        if status.lower() != "active":
            continue

        try:
            value = float(str(amount).replace("$", "").replace(",", ""))
        except:
            continue

        if category == "Income":
            income += value

        elif category == "Savings":
            savings += value

        elif category == "Bills":
            bills += value

        elif category == "Insurance":
            insurance += value

    commitments = savings + bills + insurance
    available = income - commitments

    if available >= 1000:
        health = "🟢 Excellent"

    elif available >= 500:
        health = "🟡 Comfortable"

    else:
        health = "🔴 Tight"

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

━━━━━━━━━━━━━━━━━━

💳 <b>Available Cash</b>

{money(available)}

{health}

━━━━━━━━━━━━━━━━━━

📈 <b>Allocation</b>

Savings
{savings_rate:.1f}%

Commitments
{commitment_rate:.1f}%

Available
{available_rate:.1f}%

━━━━━━━━━━━━━━━━━━

🧠 <b>Insight</b>

Your recurring commitments total {money(commitments)} each month.

You currently retain approximately {available_rate:.1f}% of your income after planned savings and recurring expenses.
"""