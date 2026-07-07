"""
ShaunMariaOS

Finance Engine
"""

from apps.database_engine import get_finance_sheet


def money(value):
    try:
        amount = float(str(value).replace("$", "").replace(",", ""))
        return f"${amount:,.2f}"
    except:
        return str(value)


def get_finance_summary():
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
        health = "🟢 Healthy"
    elif available >= 500:
        health = "🟡 Comfortable"
    else:
        health = "🔴 Tight"

    return {
        "salary": income,
        "savings": savings,
        "bills": bills,
        "insurance": insurance,
        "commitments": commitments,
        "available": available,
        "health": health,
    }


def get_finance_dashboard():
    summary = get_finance_summary()

    return f"""💰 <b>Finance Dashboard</b>

💵 Income
{money(summary["salary"])}

🏦 Savings
{money(summary["savings"])}

🧾 Bills
{money(summary["bills"])}

🛡 Insurance
{money(summary["insurance"])}

💳 Remaining
{money(summary["available"])}

{summary["health"]}"""