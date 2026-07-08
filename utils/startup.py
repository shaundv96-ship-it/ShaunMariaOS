"""
ShaunMariaOS

Startup Banner
"""

from utils.logger import logger
from app_config import (
    APP_NAME,
    APP_VERSION,
    APP_STAGE,
    APP_CODENAME,
)


def startup_banner():

    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info(f"❤️ {APP_NAME}")
    logger.info("")
    logger.info(f"Version     : {APP_VERSION}")
    logger.info(f"Stage       : {APP_STAGE}")
    logger.info(f"Codename    : {APP_CODENAME}")
    logger.info("")
    logger.info("🤖 Telegram         ✅")
    logger.info("📅 Calendar         ✅")
    logger.info("📊 Google Sheets    ✅")
    logger.info("⏰ Scheduler        ✅")
    logger.info("☁️ Railway         ✅")
    logger.info("")
    logger.info("🚀 ShaunMariaOS Ready")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")