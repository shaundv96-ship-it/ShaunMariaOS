"""
ShaunMariaOS

User Engine
"""

from apps.user_config import USERS


def get_user_profile(
    telegram_user_id: int,
) -> dict:
    profile = USERS.get(telegram_user_id)

    if profile is None:
        return {
            "name": "Unknown",
            "owner": "Unknown",
            "salary_item": "Unknown Salary",
        }

    return {
        "name": profile.get("name", "Unknown"),
        "owner": profile.get("owner", "Unknown"),
        "salary_item": profile.get(
            "salary_item",
            "Unknown Salary",
        ),
    }