"""
ShaunMariaOS

Task Category Rules
"""

import re

from apps.task_category_keywords import TASK_CATEGORY_KEYWORDS


DEFAULT_TASK_CATEGORY = "Personal"


def contains_keyword(text: str, keyword: str) -> bool:
    """Return True when a keyword appears as a complete phrase."""

    pattern = rf"\b{re.escape(keyword.casefold())}\b"

    return re.search(
        pattern,
        text.casefold(),
    ) is not None


def detect_task_category(task: str) -> str:
    """Guess the most suitable category for a task."""

    for category, keywords in TASK_CATEGORY_KEYWORDS.items():
        if any(
            contains_keyword(task, keyword)
            for keyword in keywords
        ):
            return category

    return DEFAULT_TASK_CATEGORY