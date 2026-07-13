"""
ShaunMariaOS

Natural Language Parser
"""

import re


def detect_expense(message: str):
    """
    Returns an expense dict if recognised.
    Otherwise returns None.
    """

    text = message.lower().strip()

    patterns = [

        r"spent \$?(\d+(?:\.\d+)?) on (.+)",

        r"bought (.+) \$?(\d+(?:\.\d+)?)",

        r"(.+) \$?(\d+(?:\.\d+)?)",

    ]

    for pattern in patterns:

        match = re.match(pattern, text)

        if not match:
            continue

        groups = match.groups()

        if pattern.startswith("spent"):

            amount = float(groups[0])
            item = groups[1]

        elif pattern.startswith("bought"):

            item = groups[0]
            amount = float(groups[1])

        else:

            item = groups[0]
            amount = float(groups[1])

        return {
            "amount": amount,
            "item": item.title(),
        }

    return None