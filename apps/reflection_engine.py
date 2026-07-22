"""
ShaunMariaOS

Reflection Engine
"""

from datetime import timedelta


def get_reflection(life):
    """
    Return one contextual reflection for the current moment.
    """

    finance = life["finance"]
    wedding = life["wedding"]
    calendar = life["calendar"]

    today = life["generated_at"].date()

    #
    # Wedding milestones
    #

    days = wedding.get("days_remaining", 0)

    if days == 100:
        return (
            "💍 Double digits are getting closer.\n"
            "Only 100 days until the wedding."
        )

    if days == 50:
        return (
            "💍 Just 50 days left.\n"
            "Everything is starting to feel real."
        )

    if days == 30:
        return (
            "💍 One month to go.\n"
            "The countdown is officially on."
        )

    if days == 7:
        return (
            "💍 One week left.\n"
            "Next week you'll be married."
        )

    if days == 1:
        return (
            "💍 Tomorrow is your wedding day."
        )

    #
    # Payday
    #

    tomorrow = today + timedelta(days=1)

    if tomorrow.month != today.month:
        return (
            "💰 Tomorrow is payday.\n"
            "MoneyOS will be ready once your salary is recorded."
        )

    #
    # Busy tomorrow
    #

    events = calendar.get("tomorrow_events", [])

    if len(events) >= 3:
        return (
            "📅 Tomorrow looks busy.\n"
            "Preparing tonight could make the day easier."
        )

    #
    # Finance
    #

    income = finance.get("income", 0)
    expenses = finance.get("expenses", 0)

    if income == 0 and expenses > 0:
        return (
            "💰 Your salary hasn't been logged yet this month."
        )

    if expenses == 0:
        return (
            "💰 No spending has been recorded today."
        )

    #
    # Default
    #

    return (
        "🌙 Today looked like a steady day.\n"
        "Sometimes the ordinary days are the important ones."
    )