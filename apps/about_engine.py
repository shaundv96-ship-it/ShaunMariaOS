"""
ShaunMariaOS

About Engine
"""

from app_config import (
    APP_NAME,
    APP_VERSION,
    APP_STAGE,
    OWNERS,
)

from apps.database_engine import get_spreadsheet


def get_about():

    spreadsheet = get_spreadsheet()

    owners = " ❤️ ".join(OWNERS)

    return f"""❤️ <b>{APP_NAME}</b>

━━━━━━━━━━━━━━━━━━

<b>Version</b>
v{APP_VERSION} {APP_STAGE}

<b>Owners</b>
{owners}

<b>Status</b>
🟢 Running

<b>Database</b>
{spreadsheet.title}

<b>Architecture</b>
Modular

<b>Hosting</b>
Local Development

<b>Repository</b>
GitHub Connected ✅

━━━━━━━━━━━━━━━━━━

Built with Python ❤️
"""