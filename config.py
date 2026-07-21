"""
ShaunMariaOS

Configuration Module
Loads external service settings from environment variables.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


# ==========================================================
# Core settings
# ==========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")


# ==========================================================
# Google authentication
# ==========================================================

# Railway/server authentication for Google Sheets
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_JSON"
)

# Personal OAuth authentication for local development
GOOGLE_CREDENTIALS_JSON = os.getenv(
    "GOOGLE_CREDENTIALS_JSON"
)

GOOGLE_TOKEN_JSON = os.getenv(
    "GOOGLE_TOKEN_JSON"
)


# ==========================================================
# Local authentication files
# ==========================================================

CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"


# ==========================================================
# Google API scopes
# ==========================================================

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar.readonly",
]

OAUTH_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
]

# Temporary compatibility for engines still importing SCOPES
SCOPES = OAUTH_SCOPES


# ==========================================================
# Validation
# ==========================================================

def validate_config():
    """Validate required ShaunMariaOS environment variables."""

    missing_variables = []

    if not BOT_TOKEN:
        missing_variables.append("BOT_TOKEN")

    if not GOOGLE_CALENDAR_ID:
        missing_variables.append("GOOGLE_CALENDAR_ID")

    if not GOOGLE_SHEET_ID:
        missing_variables.append("GOOGLE_SHEET_ID")

    if missing_variables:
        missing_text = ", ".join(missing_variables)

        raise ValueError(
            f"Missing required environment variables: {missing_text}"
        )


validate_config()


# ==========================================================
# Local OAuth file setup
# ==========================================================

def write_google_auth_files():
    """
    Create local OAuth files from environment variables.

    This is only required for engines using personal OAuth.
    Service-account authentication does not use these files.
    """

    if GOOGLE_CREDENTIALS_JSON:
        CREDENTIALS_FILE.write_text(
            GOOGLE_CREDENTIALS_JSON,
            encoding="utf-8",
        )
        print("credentials.json written")
    else:
        print("GOOGLE_CREDENTIALS_JSON not found")

    if GOOGLE_TOKEN_JSON:
        TOKEN_FILE.write_text(
            GOOGLE_TOKEN_JSON,
            encoding="utf-8",
        )
        print("token.json written")
    else:
        print("GOOGLE_TOKEN_JSON not found")