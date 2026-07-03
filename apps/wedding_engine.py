"""
ShaunMariaOS
Wedding Engine
"""

import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "wedding.json"


def money(amount):
    return f"${amount:,.2f}"


def load_wedding_data():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_wedding_dashboard():
    data = load_wedding_data()

    wedding_date = datetime.strptime(data["wedding_date"], "%Y-%m-%d")
    today = datetime.now()
    days_remaining = (wedding_date - today).days

    budget = data["budget"]
    details = data["key_details"]

    paid_percentage = (budget["paid"] / budget["total_budget"]) * 100
    savings_percentage = (budget["current_savings"] / budget["balance"]) * 100

    return f"""💍 <b>Shaun & Maria Wedding</b>

📅 <b>Wedding Date</b>
31 October 2026

⏳ <b>Countdown</b>
{days_remaining} days to go

⛪ <b>Church</b>
{details["church"]}

🏛️ <b>Reception</b>
{details["reception"]}

💰 <b>Budget Summary</b>
Total Budget: {money(budget["total_budget"])}
Paid: {money(budget["paid"])}
Balance: {money(budget["balance"])}

🏦 <b>Current Savings</b>
{money(budget["current_savings"])}

⚠️ <b>Shortfall</b>
{money(budget["shortfall"])}

📊 <b>Progress</b>
Paid: {paid_percentage:.1f}%
Savings vs Balance: {savings_percentage:.1f}%"""