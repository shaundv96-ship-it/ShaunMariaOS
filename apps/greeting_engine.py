"""
ShaunMariaOS

Greeting Engine
"""

from utils.time import sg_now


def get_greeting():
    hour = sg_now().hour

    if hour < 12:
        return "☀️ Good Morning Shaun & Maria"

    if hour < 18:
        return "🌤 Good Afternoon Shaun & Maria"

    if hour < 22:
        return "🌆 Good Evening Shaun & Maria"

    return "🌙 Good Night Shaun & Maria"