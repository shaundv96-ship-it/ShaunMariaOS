"""
ShaunMariaOS

Intent Engine
Determines which module should handle a message.
"""

from dataclasses import dataclass
import re
from apps.calendar_engine import normalize_calendar_text

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
    normalized_text = normalize_calendar_text(text)

    # -------------------------
    # Wedding Contribution
    # -------------------------

    wedding_contribution_patterns = (
        r"\bwedding\s+fund\b",
        r"\bwedding\s+savings?\b",
        r"\badd\b.*\bwedding\b",
        r"\bput\b.*\bwedding\b",
        r"\bcontribut(?:e|ion)\b.*\bwedding\b",
        r"\btransfer\b.*\bwedding\b",
    )

    has_wedding_contribution_phrase = any(
        re.search(pattern, text)
        for pattern in wedding_contribution_patterns
    )

    has_money_amount = bool(
        re.search(
            r"(?:"
            r"\$\s*\d[\d,]*(?:\.\d{1,2})?"
            r"|"
            r"\d[\d,]*(?:\.\d{1,2})?\s*(?:dollars?|sgd)"
            r")",
            text,
        )
    )

    if (
        has_wedding_contribution_phrase
        and has_money_amount
    ):
        return Intent(
            "wedding_contribution",
            1.0,
        )

    # -------------------------
    # Calendar
    # -------------------------

    calendar_date_pattern = re.compile(
        r"\b("
        r"today|tomorrow|"
        r"monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
        r"next\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)|"
        r"\d{1,2}\s+"
        r"(?:january|february|march|april|may|june|july|august|"
        r"september|october|november|december)"
        r"(?:\s+\d{4})?|"
        r"\d{1,2}/\d{1,2}(?:/\d{2,4})?"
        r")\b",
        flags=re.IGNORECASE,
    )

    calendar_time_pattern = re.compile(
        r"\b("
        r"\d{1,2}(?::\d{2})?\s*(?:am|pm)|"
        r"\d{1,2}\.\d{2}\s*(?:am|pm)|"
        r"\d{1,2}:\d{2}|"
        r"at\s+\d{1,2}(?::\d{2})?"
        r")\b",
        flags=re.IGNORECASE,
    )

    if (
        calendar_date_pattern.search(normalized_text)
        and calendar_time_pattern.search(normalized_text)
    ):

        return Intent("calendar", 0.98)

    calendar_query_patterns = [
    r"\bwhat('?s| is)? on\b",
    r"\bnext meeting\b",
    r"\b(am i|are we|are you)\s+free\b",
    ]

    for pattern in calendar_query_patterns:
        if re.search(
            pattern,
            text,
            re.IGNORECASE,
        ):
            return Intent(
                "calendar_query",
            0.99,
            )

    if any(
        phrase in text.lower()
        for phrase in calendar_query_patterns
    ):

        return Intent("calendar_query", 0.99)

    if re.search(
    r"\bwhat(?:'s| is)? on "
    r"(?:today|tomorrow|monday|tuesday|wednesday|"
    r"thursday|friday|saturday|sunday)\b",
    text,
    re.IGNORECASE,
    ):
        return Intent("calendar_query", 0.99)

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
        "done ",
        "complete ",
        "completed ",
    ]

    task_starters = (
        "get ",
        "buy ",
        "call ",
        "book ",
        "collect ",
        "renew ",
        "pick up ",
        "pay ",
        "buy ",
        "collect ",
        "call ",
        "text ",
        "message ",
        "visit ",
        "book ",
        "renew ",
        "submit ",
        "send ",
        "email ",
        "order ",
    )

    contains_amount = bool(
        re.search(
            r"(?:\$\s*\d+(?:\.\d{1,2})?"
            r"|\d+(?:\.\d{1,2})?\s*(?:dollars?|sgd))",
            text,
        )
    )

    if (
        any(phrase in text for phrase in task_phrases)
        or (
            text.startswith(task_starters)
            and not contains_amount
        )
    ):
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
