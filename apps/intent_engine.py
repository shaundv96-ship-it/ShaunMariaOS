"""
ShaunMariaOS

Intent Engine
Determines which module should handle a message.
"""

from dataclasses import dataclass
import re

from apps.calendar_parser import (
    normalize_calendar_text,
    parse_calendar_event,
)


@dataclass
class Intent:
    name: str
    confidence: float = 1.0


def detect_intent(
    text: str,
) -> Intent:
    """
    Detect which ShaunMariaOS module should handle
    the user's message.
    """

    text = text.strip().casefold()
    normalized_text = normalize_calendar_text(text)

    # =====================================================
    # Wedding Contribution
    # =====================================================

    short_wedding_contribution = bool(
        re.fullmatch(
            r"(?:(?:shaun|maria)(?:'s)?\s+)?"
            r"wedding\s+\$?\s*"
            r"\d[\d,]*(?:\.\d{1,2})?",
            text,
            re.IGNORECASE,
        )
    )

    if short_wedding_contribution:
        return Intent(
            "wedding_contribution",
            1.0,
        )

    wedding_contribution_patterns = (
        r"\bwedding\s+fund\b",
        r"\bwedding\s+savings?\b",
        r"\badd\b.*\bwedding\b",
        r"\bput\b.*\bwedding\b",
        r"\bcontribut(?:e|ion)\b.*\bwedding\b",
        r"\btransfer\b.*\bwedding\b",
    )

    has_wedding_contribution_phrase = any(
        re.search(
            pattern,
            text,
        )
        for pattern in wedding_contribution_patterns
    )

    has_money_amount = bool(
        re.search(
            r"(?:"
            r"\$\s*\d[\d,]*(?:\.\d{1,2})?"
            r"|"
            r"\d[\d,]*(?:\.\d{1,2})?"
            r"\s*(?:dollars?|sgd)"
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

       # =====================================================
    # Calendar Query
    # =====================================================

    calendar_query_patterns = (
        r"\bwhat(?:'s| is)?\s+on\b",
        r"\bnext\s+meeting\b",
        r"\b(?:am\s+i|are\s+we|are\s+you)\s+free\b",
    )

    if any(
        re.search(
            pattern,
            normalized_text,
            re.IGNORECASE,
        )
        for pattern in calendar_query_patterns
    ):
        return Intent(
            "calendar_query",
            0.99,
        )

    # =====================================================
    # Calendar Delete
    # =====================================================

    if re.match(
        r"^\s*(?:cancel|delete|remove)\s+\S+",
        text,
        re.IGNORECASE,
    ):
        return Intent(
            "calendar_delete",
            0.99,
        )
    # =====================================================
    # Calendar Update
    # =====================================================

    if re.match(
        r"^\s*(?:move|change|reschedule|rename)\s+\S+",
        text,
        re.IGNORECASE,
    ):
        return Intent(
            "calendar_update",
            0.99,
        )
    # =====================================================
    # Calendar Event
    # =====================================================

    if parse_calendar_event(
        normalized_text
    ) is not None:
        return Intent(
            "calendar",
            0.98,
        )

    # =====================================================
    # Income
    # =====================================================

    income_keywords = (
        "salary",
        "bonus",
        "allowance",
        "commission",
        "income",
        "payday",
    )

    if any(
        keyword in text
        for keyword in income_keywords
    ):
        return Intent(
            "income",
            0.95,
        )

     # =====================================================
    # Task
    # =====================================================

    task_phrases = (
        "need to",
        "remember to",
        "remind me",
        "todo",
        "to do",
        "task",
        "done ",
        "complete ",
        "completed ",
    )

    task_starters = (
        "get ",
        "buy ",
        "call ",
        "book ",
        "collect ",
        "renew ",
        "pick up ",
        "pay ",
        "text ",
        "message ",
        "visit ",
        "submit ",
        "send ",
        "email ",
        "order ",
    )

    contains_amount = bool(
        re.search(
            r"(?:"
            r"\$\s*\d[\d,]*(?:\.\d{1,2})?"
            r"|"
            r"\d[\d,]*(?:\.\d{1,2})?"
            r"\s*(?:dollars?|sgd)"
            r")",
            text,
        )
    )

    if (
        any(
            phrase in text
            for phrase in task_phrases
        )
        or (
            text.startswith(
                task_starters
            )
            and not contains_amount
        )
    ):
        return Intent(
            "task",
            0.90,
        )


    # =====================================================
    # Wedding
    # =====================================================

    wedding_keywords = (
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
    )

    if any(
        keyword in text
        for keyword in wedding_keywords
    ):
        return Intent(
            "wedding",
            0.90,
        )

   
    # =====================================================
    # Expense
    # =====================================================

    has_amount = bool(
        re.search(
            r"(?:"
            r"\$\s*\d[\d,]*(?:\.\d{1,2})?"
            r"|"
            r"\d[\d,]*(?:\.\d{1,2})?"
            r"\s*(?:dollars?|sgd)"
            r")",
            text,
        )
    )

    expense_keywords = (
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
    )

    has_expense_keyword = any(
        keyword in text
        for keyword in expense_keywords
    )

    if (
        has_amount
        or has_expense_keyword
    ):
        return Intent(
            "expense",
            0.95,
        )

    return Intent(
        "unknown",
        0.0,
    )