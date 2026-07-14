"""
ShaunMariaOS

Intent Engine
Determines which module should handle a message.
"""

from dataclasses import dataclass
import re


@dataclass
class Intent:
    name: str
    confidence: float = 1.0


def detect_intent(text: str) -> Intent:
    """
    Detect which ShaunMariaOS module should
    handle the user's message.
    """

    text = text.lower().strip()

    # -------------------------
    # Income
    # -------------------------

    income_keywords = [
        "salary",
        "bonus",
        "allowance",
        "commission",
        "income",
        "payday",
    ]

    if any(keyword in text for keyword in income_keywords):
        return Intent("income", 0.95)

    # -------------------------
    # Wedding
    # -------------------------

    wedding_keywords = [
        "wedding",
        "florist",
        "bridal",
        "photographer",
        "videographer",
        "church",
        "banquet",
        "venue",
        "gown",
        "sherwani",
    ]

    if any(keyword in text for keyword in wedding_keywords):
        return Intent("wedding", 0.90)

    # -------------------------
    # Task
    # -------------------------

    task_phrases = [
        "need to",
        "remember to",
        "remind me",
        "todo",
        "to do",
        "task",
    ]

    if any(phrase in text for phrase in task_phrases):
        return Intent("task", 0.90)

    # -------------------------
    # Expense
    # -------------------------

    has_amount = bool(
        re.search(
            r"(?:\$\s*\d+(?:\.\d{1,2})?|\d+(?:\.\d{1,2})?\s*(?:dollars?|sgd))",
            text,
        )
    )

    expense_keywords = [
        "spent",
        "paid",
        "bought",
        "grab",
        "gojek",
        "lunch",
        "dinner",
        "breakfast",
        "coffee",
        "haircut",
        "clinic",
        "ntuc",
        "fairprice",
        "giant",
        "sheng siong",
    ]

    has_expense_keyword = any(
        keyword in text
        for keyword in expense_keywords
    )

    if has_amount or has_expense_keyword:
        return Intent("expense", 0.95)

    return Intent("unknown", 0.0)
