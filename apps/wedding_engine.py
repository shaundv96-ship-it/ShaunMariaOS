"""
ShaunMariaOS

Wedding Engine
"""

from datetime import datetime

from apps.database_engine import get_budget_sheet


def money(value):
    try:
        amount = float(str(value).replace("$", "").replace(",", "").strip())
        return f"${amount:,.2f}"
    except ValueError:
        return str(value)


def find_row_containing(rows, text):
    for row in rows:
        for cell in row:
            if text.lower() in str(cell).lower():
                return row
    return None


def get_wedding_dashboard():
    wedding_date = datetime(2026, 10, 31)
    today = datetime.now()
    days_remaining = (wedding_date - today).days

    return f"""💍 <b>Shaun & Maria Wedding</b>

📅 <b>Wedding Date</b>
31 October 2026

⏳ <b>Countdown</b>
{days_remaining} days to go

Commands:
/weddingbudget - Budget summary"""


def get_wedding_budget():
    rows = get_budget_sheet()

    totals_row = None
    for row in rows:
        if any("45,444" in str(cell) or "45444" in str(cell) for cell in row):
            totals_row = row
            break

    savings_row = find_row_containing(rows, "Current Savings")
    shortfall_row = find_row_containing(rows, "Shortfall")

    if not totals_row:
        return "⚠️ Could not find budget totals in the Budget sheet."

    total_budget = totals_row[1] if len(totals_row) > 1 else "-"
    paid = totals_row[2] if len(totals_row) > 2 else "-"
    balance = totals_row[3] if len(totals_row) > 3 else "-"

    current_savings = savings_row[1] if savings_row and len(savings_row) > 1 else "-"
    shortfall = shortfall_row[1] if shortfall_row and len(shortfall_row) > 1 else "-"

    return f"""💰 <b>Wedding Budget</b>

💍 <b>Total Budget</b>
{money(total_budget)}

✅ <b>Paid</b>
{money(paid)}

📉 <b>Balance</b>
{money(balance)}

🏦 <b>Current Savings</b>
{money(current_savings)}

⚠️ <b>Shortfall</b>
{money(shortfall)}

📊 <b>Source</b>
Live from Google Sheets"""