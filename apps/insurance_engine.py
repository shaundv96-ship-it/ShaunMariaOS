"""
ShaunMariaOS

Insurance Engine
"""

from apps.database_engine import get_finance_sheet


def money(value):
    try:
        amount = float(str(value).replace("$", "").replace(",", ""))
        return f"${amount:,.2f}"
    except:
        return str(value)


def get_insurance_dashboard():

    rows = get_finance_sheet()

    policies = []
    total = 0

    for row in rows:

        if len(row) < 9:
            continue

        category = str(row[1]).strip()
        item = row[2]
        owner = row[3]
        amount = row[4]
        due = row[5]
        frequency = row[6]
        status = row[8]

        if category != "Insurance":
            continue

        try:
            value = float(str(amount).replace("$", "").replace(",", ""))
            total += value
        except:
            value = 0

        policies.append({
            "item": item,
            "owner": owner,
            "amount": amount,
            "due": due,
            "frequency": frequency,
            "status": status
        })

    message = "🛡 <b>Insurance Dashboard</b>\n\n"

    if not policies:
        return message + "No insurance policies found."

    for policy in policies:

        icon = "🟢" if str(policy["status"]).lower() == "active" else "🔴"

        message += f"""📄 <b>{policy['item']}</b>

💰 {money(policy['amount'])}
👤 {policy['owner']}
📅 {policy['due']}
🔁 {policy['frequency']}
{icon} {policy['status']}

"""

    message += "━━━━━━━━━━━━━━━━━━\n\n"

    message += f"""💵 <b>Total Insurance</b>

{money(total)}

━━━━━━━━━━━━━━━━━━

🧠 <b>Insight</b>

Your insurance commitments total {money(total)} per month.

All active policies are included in your monthly cash flow planning.
"""

    return message