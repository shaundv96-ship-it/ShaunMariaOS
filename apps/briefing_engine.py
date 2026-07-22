"""
ShaunMariaOS

Briefing Engine
"""

from utils.time import sg_now

from apps.greeting_engine import get_greeting
from apps.life_engine import get_life_snapshot
from apps.formatting_engine import money


def get_daily_briefing():
    life = get_life_snapshot()

    finance = life["finance"]
    wedding = life["wedding"]
    calendar = life["calendar"]

    today = sg_now().strftime("%A, %d %B %Y")

    advice = life["advisor"]
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