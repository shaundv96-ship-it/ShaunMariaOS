"""
ShaunMariaOS

Application Configuration
"""

import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "ShaunMariaOS"
APP_VERSION = "1.4.0"
APP_STAGE = "Alpha"
APP_CODENAME = "Foundation"

OWNERS = ["Shaun", "Maria"]

DEBUG = os.getenv("DEBUG", "true").lower() == "true"
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "0"))

WEDDING_DATE = datetime(2026, 10, 31)

HOME_NAME = "OakVille @ AMK"
HOME_TOP = "Q3 2030"

CURRENCY = "$"