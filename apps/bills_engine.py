"""
ShaunMariaOS

Bills Engine
"""

from apps.database_engine import get_finance_sheet


def money(value):
    try:
        amount = float(str(value).replace("$", "").replace(",", ""))
        return f"${amount:,.2f}"
    except:
        return str(value)


def get_bills_dashboard():

    rows = get_finance_sheet()

    bills = []

    total = 0

    for row in rows:

        if len(row) < 9:
            continue

        category = str(row[1]).strip()
        item = str(row[2]).strip()
        amount = row[4]
        due = str(row[5]).strip()
        priority = str(row[7]).strip()
        status = str(row[8]).strip()

        if category != "Bills":
            continue

        if status.lower() != "active":
            continue

        try:
            value = float(str(amount).replace("$", "").replace(",", ""))
        except:
            continue

        total += value

        bills.append({
            "item": item,
            "amount": value,
            "due": due,
            "priority": priority
        })

    priority_order = {
        "HIGH": 0,
        "MEDIUM": 1,
        "LOW": 2
    }

    bills.sort(
        key=lambda x: priority_order.get(
            x["priority"].upper(),
            99
        )
    )

    message = "🧾 <b>Bills Dashboard</b>\n\n"

    message += f"💰 <b>Total Monthly Bills</b>\n{money(total)}\n\n"

    message += "📅 <b>Active Bills</b>\n"

    for bill in bills:

        emoji = {
            "HIGH": "🔴",
            "MEDIUM": "🟡",
            "LOW": "🟢"
        }.get(bill["priority"].upper(), "⚪")

        message += (
            f"\n{emoji} <b>{bill['item']}</b>\n"
            f"{money(bill['amount'])}\n"
            f"{bill['due']}\n"
        )

    message += "\n📊 <b>Source</b>\nLive from Google Sheets"

    return message