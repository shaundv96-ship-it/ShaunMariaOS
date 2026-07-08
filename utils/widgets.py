"""
ShaunMariaOS

UI Widgets
"""


def status_widget(title, status):
    return (f"{title}", status)


def metric_widget(title, value):
    return (f"{title}", value)


def countdown_widget(title, days):
    return (f"⏳ {title}", f"{days} days remaining")


def money_widget(title, amount):
    return (f"💰 {title}", amount)


def info_widget(title, value):
    return (title, value)