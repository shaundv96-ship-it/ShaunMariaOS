"""
ShaunMariaOS

Natural Language Parser
"""

import re


def detect_expense(message: str):
    """
    Detect natural language expense entries.
    """

    text = message.lower().strip()

    patterns = [

        # Spent $18.50 on lunch
        r"spent \$?(\d+(?:\.\d+)?) on (.+)",

        # Bought coffee $5
        r"bought (.+) \$?(\d+(?:\.\d+)?)",

        # $6 lunch
        r"\$?(\d+(?:\.\d+)?) (.+)",

        # lunch $6
        r"(.+) \$?(\d+(?:\.\d+)?)",
    ]

    for index, pattern in enumerate(patterns):

        match = re.fullmatch(pattern, text)

        if not match:
            continue

        first, second = match.groups()

        if index == 0:
            amount = float(first)
            item = second

        elif index == 1:
            item = first
            amount = float(second)

        elif index == 2:
            amount = float(first)
            item = second

        else:
            item = first
            amount = float(second)

        return {
            "amount": amount,
            "item": item.strip().title(),
        }

    return None