"""
ShaunMariaOS

UI Helpers
"""

SEPARATOR = "━━━━━━━━━━━━━━━━━━"


def build_screen(title, sections=None, footer=None):
    message = f"{title}\n\n{SEPARATOR}\n"

    if sections:
        for heading, body in sections:
            message += f"\n<b>{heading}</b>\n{body}\n"
            message += f"\n{SEPARATOR}\n"

    if footer:
        message += f"\n{footer}"

    return message