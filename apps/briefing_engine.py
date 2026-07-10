"""
ShaunMariaOS

Briefing Engine
"""

from utils.time import sg_now

from apps.greeting_engine import get_greeting
from apps.summary_engine import get_system_summary
from apps.advisor_engine import get_advisor
from apps.formatting_engine import money


def get_daily_briefing():
    summary = get_system_summary()

    finance = summary["finance"]
    wedding = summary["wedding"]
    calendar = summary["calendar"]

    today = sg_now().strftime("%A, %d %B %Y")

    advice = get_advisor()
    advice_text = (
        "\n".join(f"• {item}" for item in advice)
        if advice
        else "Everything looks good today."
    )

    return f"""🌅 <b>Daily Briefing</b>

{get_greeting()}

📅 {today}

━━━━━━━━━━━━━━━━━━

💍 <b>Wedding</b>

⏳ {wedding["days_remaining"]} days remaining

💰 Balance
{money(wedding["balance"])}

━━━━━━━━━━━━━━━━━━

💰 <b>Finance</b>

Available Cash
{money(finance["available"])}

{finance["health"]}

━━━━━━━━━━━━━━━━━━

📅 <b>Today's Schedule</b>

{calendar["next_event"]}

━━━━━━━━━━━━━━━━━━

🧠 <b>Advisor</b>

{advice_text}

━━━━━━━━━━━━━━━━━━

❤️ Have a wonderful day, Shaun & Maria.
"""