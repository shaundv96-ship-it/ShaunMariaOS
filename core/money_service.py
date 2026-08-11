"""
ShaunMariaOS

Money Service
Reusable MoneyOS business logic for Telegram, web, and future app clients.
"""

from dataclasses import dataclass

from apps.money_engine import get_money_summary


@dataclass
class MoneySummaryResult:
    """Structured MoneyOS summary for any client."""

    success: bool
    status: str
    message: str
    income: float = 0.0
    expenses: float = 0.0
    allocated: float = 0.0
    monthly_cash_flow: float = 0.0
    available_money: float = 0.0
    savings: float = 0.0
    bills: float = 0.0
    insurance: float = 0.0
    wedding_fund: float = 0.0
    health: str = "Unknown"


def get_money_overview(
    *,
    force_refresh: bool = False,
) -> MoneySummaryResult:
    """
    Return a client-independent MoneyOS overview.

    Telegram, APIs, and the future app can all consume
    the same structured result.
    """

    try:
        summary = get_money_summary(
            force_refresh=force_refresh,
        )

        return MoneySummaryResult(
            success=True,
            status="ok",
            message="Money overview loaded.",
            income=float(
                summary.get("income", 0.0)
            ),
            expenses=float(
                summary.get("expenses", 0.0)
            ),
            allocated=float(
                summary.get("allocated", 0.0)
            ),
            monthly_cash_flow=float(
                summary.get(
                    "monthly_cash_flow",
                    0.0,
                )
            ),
            available_money=float(
                summary.get(
                    "available_money",
                    0.0,
                )
            ),
            savings=float(
                summary.get("savings", 0.0)
            ),
            bills=float(
                summary.get("bills", 0.0)
            ),
            insurance=float(
                summary.get("insurance", 0.0)
            ),
            wedding_fund=float(
                summary.get(
                    "allocations",
                    {},
                ).get(
                    "Wedding Fund",
                    0.0,
                )
            ),
            health=str(
                summary.get(
                    "health",
                    "Unknown",
                )
            ),
        )

    except Exception as error:
        return MoneySummaryResult(
            success=False,
            status="error",
            message=str(error),
        )