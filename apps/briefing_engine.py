"""
ShaunMariaOS

Briefing Engine
"""

from apps.dashboard_engine import get_dashboard_message
from utils.time import sg_now

now = sg_now()

def get_daily_briefing():
    dashboard = get_dashboard_message()

    return f"""🌅 <b>Daily Briefing</b>

{dashboard}

━━━━━━━━━━━━━━━━━━

🎯 <b>Today’s Focus</b>

• Review calendar
• Check finance snapshot
• Keep wedding planning on track

❤️ Have a good day, Shaun & Maria"""