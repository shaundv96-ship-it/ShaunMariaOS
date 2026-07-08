"""
ShaunMariaOS

Version Engine
"""

from app_config import APP_NAME, APP_VERSION, APP_STAGE, APP_CODENAME
from utils.ui import build_screen
from utils.widgets import info_widget


def get_version():

    sections = [
        info_widget("🚀 Version", f"v{APP_VERSION}"),
        info_widget("🏷 Stage", APP_STAGE),
        info_widget("✨ Codename", APP_CODENAME),
        info_widget("☁️ Platform", "Railway"),
        info_widget("🤖 Telegram", "🟢 Connected"),
    ]

    return build_screen(
        f"❤️ <b>{APP_NAME}</b>",
        sections,
        "Always On 🚀",
    )