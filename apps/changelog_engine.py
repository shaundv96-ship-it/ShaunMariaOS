"""
ShaunMariaOS

Changelog Engine
"""

from pathlib import Path


CHANGELOG_FILE = Path("docs/CHANGELOG.md")


def get_changelog_dashboard():
    """
    Returns the contents of CHANGELOG.md formatted for Telegram.
    """

    if not CHANGELOG_FILE.exists():
        return "⚠️ CHANGELOG.md not found."

    try:
        content = CHANGELOG_FILE.read_text(encoding="utf-8")

        # Telegram supports HTML, not Markdown.
        # Wrap the markdown inside <pre> so it stays nicely formatted.
        return f"<pre>{content}</pre>"

    except Exception as e:
        return f"⚠️ Unable to load changelog.\n\n{e}"