"""
ShaunMariaOS

Formatting Engine
"""


def money(value):
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


def percent(value):
    try:
        return f"{float(value):.1f}%"
    except (ValueError, TypeError):
        return "0.0%"