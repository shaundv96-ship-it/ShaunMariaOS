"""
ShaunMariaOS

Version Engine
"""

from app_config import (
    APP_NAME,
    APP_VERSION,
    APP_STAGE,
    APP_CODENAME,
)


def get_version():

    return f"""
❤️ <b>{APP_NAME}</b>

🚀 Version
{APP_VERSION}

🏷 Stage
{APP_STAGE}

✨ Codename
{APP_CODENAME}

☁️ Environment
Production

🖥 Platform
Railway

🤖 Telegram
Connected
"""