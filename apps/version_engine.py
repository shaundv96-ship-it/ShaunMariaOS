"""
ShaunMariaOS

Version Engine
"""

from app_config import APP_NAME, APP_VERSION, APP_STAGE, APP_CODENAME
from utils.ui import build_screen


def get_version():
    sections = [
        ("🚀 Version", f"v{APP_VERSION}"),
        ("🏷 Stage", APP_STAGE),
        ("✨ Codename", APP_CODENAME),
        ("☁️ Platform", "Railway"),
        ("🤖 Telegram", "🟢 Connected"),
    ]

    return build_screen(
        f"❤️ <b>{APP_NAME}</b>",
        sections,
        "Always On 🚀",
    )