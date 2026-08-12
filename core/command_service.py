"""
ShaunMariaOS

Command Service
Routes natural-language commands to the correct Core service.
"""

from dataclasses import dataclass
import re
from typing import Any

from apps.intent_engine import detect_intent
from apps.wedding_engine import add_wedding_contribution

from core.calendar_service import create_event_from_text
from core.task_service import create_task_from_text
from core.money_action_service import (
    record_expense_from_text,
    record_income_from_text,
)

from utils.nlp_parser import detect_wedding_contribution


@dataclass
class CommandResult:
    """Structured result returned by the global command router."""

    success: bool
    status: str
    message: str
    intent: str
    data: dict[str, Any] | None = None


def get_wedding_contributor(
    text: str,
) -> str | None:
    """Identify Shaun or Maria from a wedding contribution."""

    lowered = text.casefold()

    if re.search(
        r"\bshaun(?:'s)?\b",
        lowered,
    ):
        return "Shaun"

    if re.search(
        r"\bmaria(?:'s)?\b",
        lowered,
    ):
        return "Maria"

    return None

def clean_wedding_contribution_text(
    text: str,
) -> str:
    """
    Remove an explicit contributor name before
    passing the command to the existing wedding parser.
    """

    cleaned = re.sub(
        r"^\s*(?:shaun|maria)(?:'s)?\s+",
        "",
        text,
        count=1,
        flags=re.IGNORECASE,
    )

    return cleaned.strip()

def run_command(
    text: str,
) -> CommandResult:
    """
    Route natural-language input to the correct ShaunMariaOS service.

    Supported:
        Wedding contributions
        Calendar
        Tasks
        Expenses
        Income
    """

    text = text.strip()

    if not text:
        return CommandResult(
            success=False,
            status="empty",
            message="Tell me what you'd like to do.",
            intent="unknown",
        )

    intent = detect_intent(text)

    # =====================================================
    # Wedding Contribution
    # =====================================================

    if intent.name == "wedding_contribution":
        contribution_text = (
            clean_wedding_contribution_text(
                text
            )
        )

        detected = detect_wedding_contribution(
            contribution_text
        )

        if not detected:
            return CommandResult(
                success=False,
                status="invalid",
                message=(
                    "I couldn't find the wedding contribution amount."
                ),
                intent="wedding_contribution",
            )

        contributor = get_wedding_contributor(
            text
        )

        if not contributor:
            return CommandResult(
                success=False,
                status="owner_required",
                message=(
                    "Whose wedding contribution is this? "
                    "Try: Shaun Wedding $1300 "
                    "or Maria Wedding $1000."
                ),
                intent="wedding_contribution",
            )

        try:
            result = add_wedding_contribution(
                detected["amount"]
            )

            return CommandResult(
                success=True,
                status="updated",
                message="Wedding fund updated.",
                intent="wedding_contribution",
                data={
                    "contributor": contributor,
                    **result,
                },
            )

        except Exception as exc:
            return CommandResult(
                success=False,
                status="error",
                message=str(exc),
                intent="wedding_contribution",
            )

    # =====================================================
    # Calendar
    # =====================================================

    if intent.name == "calendar":
        result = create_event_from_text(
            text
        )

        return CommandResult(
            success=result.success,
            status=result.status,
            message=result.message,
            intent="calendar",
            data={
                "parsed_event": result.parsed_event,
                "created_event": result.created_event,
            },
        )

    # =====================================================
    # Task
    # =====================================================

    if intent.name == "task":
        result = create_task_from_text(
            text
        )

        return CommandResult(
            success=result.success,
            status=result.status,
            message=result.message,
            intent="task",
            data={
                "task": result.task,
            },
        )

    # =====================================================
    # Expense
    # =====================================================

    if intent.name == "expense":
        result = record_expense_from_text(
            text
        )

        return CommandResult(
            success=result.success,
            status=result.status,
            message=result.message,
            intent="expense",
            data=result.data,
        )

    # =====================================================
    # Income
    # =====================================================

    if intent.name == "income":
        result = record_income_from_text(
            text
        )

        return CommandResult(
            success=result.success,
            status=result.status,
            message=result.message,
            intent="income",
            data=result.data,
        )

    # =====================================================
    # Unsupported
    # =====================================================

    return CommandResult(
        success=False,
        status="unsupported",
        message=(
            "I understood the request, but this action "
            "isn't connected to the app yet."
        ),
        intent=intent.name,
    )