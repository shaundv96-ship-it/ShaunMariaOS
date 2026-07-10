"""
ShaunMariaOS

Status Engine
"""


def finance_status(available):
    """Return the financial health status."""

    if available >= 1500:
        return "🟢 Excellent"

    if available >= 1000:
        return "🟢 Healthy"

    if available >= 500:
        return "🟡 Comfortable"

    if available >= 0:
        return "🟠 Watch Closely"

    return "🔴 Action Required"


def wedding_status(paid_percentage):
    """Return wedding budget status."""

    if paid_percentage >= 90:
        return "🟢 Nearly Complete"

    if paid_percentage >= 70:
        return "🟢 On Track"

    if paid_percentage >= 50:
        return "🟡 Progressing"

    if paid_percentage >= 25:
        return "🟠 Needs Attention"

    return "🔴 Just Started"