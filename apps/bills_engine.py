"""
ShaunMariaOS

Bills Engine
"""

from apps.formatting_engine import money
from utils.sheet_parser import get_bills_summary


def get_bills_dashboard():
    summary = get_bills_summary()

    message = f"""🧾 <b>Bills Dashboard</b>

💰 <b>Total Monthly Bills</b>
{money(summary["total"])}

📅 <b>Active Bills</b>
"""

    icons = {
        "HIGH": "🔴",
        "MEDIUM": "🟡",
        "LOW": "🟢",
    }

    for bill in summary["bills"]:
        message += f"""

{icons.get(bill["priority"], "⚪")} <b>{bill["item"]}</b>
{money(bill["amount"])}
{bill["due"]}
"""

    message += """

📊 <b>Source</b>
Live from Google Sheets"""

    return message