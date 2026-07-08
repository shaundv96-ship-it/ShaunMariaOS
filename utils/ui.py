"""
ShaunMariaOS

UI Builder
"""

SEPARATOR = "━━━━━━━━━━━━━━━━━━"


def build_screen(title, sections=None, footer=None):

    lines = [title, "", SEPARATOR]

    if sections:
        for heading, body in sections:
            lines.append("")
            lines.append(f"<b>{heading}</b>")
            lines.append(body)

    if footer:
        lines.append("")
        lines.append(SEPARATOR)
        lines.append("")
        lines.append(footer)

    return "\n".join(lines)