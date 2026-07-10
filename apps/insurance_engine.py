"""
ShaunMariaOS

Insurance Engine
"""

from apps.formatting_engine import money
from utils.sheet_parser import get_insurance_summary


def get_insurance_dashboard():
    summary = get_insurance_summary()
    policies = summary["policies"]

    if not policies:
        return """🛡 <b>Insurance Dashboard</b>

No insurance policies found."""

    lines = [
        "🛡 <b>Insurance Dashboard</b>",
        "",
    ]

    for policy in policies:
        icon = "🟢" if policy["is_active"] else "🔴"

        lines.extend(
            [
                f"📄 <b>{policy['item']}</b>",
                f"💰 {money(policy['amount'])}",
                f"👤 {policy['owner'] or 'Not specified'}",
                f"📅 {policy['due'] or 'No due date'}",
                f"🔁 {policy['frequency'] or 'Not specified'}",
                f"{icon} {policy['status'] or 'Unknown'}",
                "",
            ]
        )

    lines.extend(
        [
            "━━━━━━━━━━━━━━━━━━",
            "",
            "💵 <b>Active Insurance Commitments</b>",
            money(summary["active_total"]),
            "",
            "📊 <b>Policies</b>",
            (
                f"{summary['active_count']} active "
                f"out of {summary['policy_count']}"
            ),
            "",
            "━━━━━━━━━━━━━━━━━━",
            "",
            "🧠 <b>Insight</b>",
            (
                f"Active insurance commitments total "
                f"{money(summary['active_total'])} each month."
            ),
            "",
            "Active policies are included in monthly cash-flow planning.",
            "",
            "📈 <b>Source</b>",
            "Live from Google Sheets",
        ]
    )

    return "\n".join(lines)