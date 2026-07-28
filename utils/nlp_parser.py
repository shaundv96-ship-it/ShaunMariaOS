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

def detect_wedding_contribution(message: str):
    """
    Detect wedding savings contributions.

    Examples:
        Wedding fund $1000
        Wedding fund $1,000
        Wedding savings $500
        Add $300 to wedding
        Put $450 into wedding
        Transfer SGD 800 to wedding
    """

    text = message.lower().strip()

    amount_pattern = (
        r"(?:\$\s*|sgd\s*)?"
        r"([\d,]+(?:\.\d{1,2})?)"
        r"(?:\s*dollars?)?"
    )

    patterns = [
        rf"wedding fund\s+{amount_pattern}",
        rf"wedding savings\s+{amount_pattern}",
        rf"add\s+{amount_pattern}\s+to wedding(?: fund| savings)?",
        rf"put\s+{amount_pattern}\s+into wedding(?: fund| savings)?",
        rf"transfer\s+{amount_pattern}\s+to wedding(?: fund| savings)?",
    ]

    for pattern in patterns:
        match = re.fullmatch(pattern, text)

        if not match:
            continue

        amount_text = match.group(1)

        return {
            "amount": float(
                amount_text.replace(",", "")
            )
        }

    return None