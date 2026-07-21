"""
ShaunMariaOS

Google Authentication Engine

Provides shared Google credentials for all Google services
(Sheets, Calendar, Drive, Gmail, etc.)
"""

import json
import logging
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as UserCredentials
from google.oauth2.service_account import Credentials as ServiceCredentials
from google_auth_oauthlib.flow import InstalledAppFlow

from config import (
    GOOGLE_SCOPES,
    GOOGLE_SERVICE_ACCOUNT_JSON,
)

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"


def get_local_credentials():
    """
    Authenticate using OAuth for local development.
    """

    credentials = None

    if TOKEN_FILE.exists():
        credentials = UserCredentials.from_authorized_user_file(
            TOKEN_FILE,
            GOOGLE_SCOPES,
        )

    if not credentials or not credentials.valid:

        if (
            credentials
            and credentials.expired
            and credentials.refresh_token
        ):
            credentials.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                GOOGLE_SCOPES,
            )

            credentials = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(
            credentials.to_json(),
            encoding="utf-8",
        )

    logger.info("Google authentication: local OAuth")

    return credentials


def get_service_account_credentials():
    """
    Authenticate using Railway service account.
    """

    if not GOOGLE_SERVICE_ACCOUNT_JSON:
        return None

    credentials_info = json.loads(
        GOOGLE_SERVICE_ACCOUNT_JSON
    )

    logger.info("Google authentication: service account")

    return ServiceCredentials.from_service_account_info(
        credentials_info,
        scopes=GOOGLE_SCOPES,
    )


def get_google_credentials():
    """
    Return the correct credentials depending on environment.

    Railway -> Service Account
    Local -> OAuth
    """

    service_credentials = get_service_account_credentials()

    if service_credentials:
        return service_credentials

    return get_local_credentials()