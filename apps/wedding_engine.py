"""
ShaunMariaOS
Wedding Engine
"""

from datetime import datetime
from apps.sheets_engine import get_worksheet_values


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

Use:
/weddingbudget - Budget summary"""


def get_wedding_budget():
    rows = get_worksheet_values("Budget")

    total_row = find_row_containing(rows, "Current Savings")
    shortfall_row = find_row_containing(rows, "11,861")

    # From your sheet structure:
    # totals are around row with $45,444 / $19,662.40 / $25,861.60
    totals_row = None
    for row in rows:
        if "$45,444" in row or "45,444" in row:
            totals_row = row
            break

    if not totals_row:
        return "⚠️ Could not find budget totals in the Budget sheet."

    total_budget = totals_row[1] if len(totals_row) > 1 else "-"
    paid = totals_row[2] if len(totals_row) > 2 else "-"
    balance = totals_row[3] if len(totals_row) > 3 else "-"

    current_savings = "-"
    if total_row and len(total_row) > 1:
        current_savings = total_row[1]

    shortfall = "-"
    if shortfall_row:
        for cell in shortfall_row:
            if "11,861" in str(cell):
                shortfall = cell
                break

    message = f"""💰 <b>Wedding Budget</b>

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

    return message