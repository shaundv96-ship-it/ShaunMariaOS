"""
ShaunMariaOS

Dashboard Engine
"""

from datetime import datetime

from apps.finance_engine import get_finance_summary
from apps.wedding_engine import get_wedding_summary
from apps.calendar_engine import get_calendar_summary


VERSION = "v1.0 Alpha"


def get_greeting():

    hour = datetime.now().hour

    if hour < 12:
        return "☀️ Good Morning Shaun"

    elif hour < 18:
        return "🌤 Good Afternoon Shaun"

    elif hour < 22:
        return "🌆 Good Evening Shaun"

    return "🌙 Good Night Shaun"


def get_dashboard_message():

    finance = get_finance_summary()
    wedding = get_wedding_summary()
    calendar = get_calendar_summary()

    today = datetime.now().strftime("%A, %d %B %Y")

    message = f"""❤️ <b>ShaunMariaOS</b>

{get_greeting()}

📅 {today}

━━━━━━━━━━━━━━━━━━

💒 <b>Wedding</b>

⏳ {wedding['days_remaining']} days remaining

👥 Guests
{wedding['guest_total']}

💰 Budget
{wedding['paid_percentage']:.1f}% Paid

━━━━━━━━━━━━━━━━━━

💵 <b>Finance</b>

Salary
${finance['salary']:,.2f}

Available
${finance['available']:,.2f}

{finance['health']}

━━━━━━━━━━━━━━━━━━

📅 <b>Today</b>

{calendar['next_event']}

━━━━━━━━━━━━━━━━━━

🏠 <b>Home</b>

OakVille @ AMK

Status
Booked ✅

TOP
Q3 2030

━━━━━━━━━━━━━━━━━━

🧠 <b>Quick Insight</b>
"""

    # ---------- AI Insight ----------

    insights = []

    if finance["available"] >= 1000:
        insights.append("💰 Cash flow is healthy.")

    if wedding["seats_available"] != "-":
        insights.append(
            f"💒 {wedding['seats_available']} wedding seats remaining."
        )

    if calendar["event_count"] == 0:
        insights.append("📅 No calendar events today.")

    if wedding["paid_percentage"] >= 40:
        insights.append("✅ Wedding budget is progressing well.")

    if not insights:
        insights.append("Everything looks good today.")

    for item in insights:
        message += f"\n• {item}"

    message += f"""

━━━━━━━━━━━━━━━━━━

❤️ {VERSION}
"""

    return message