"""
ShaunMariaOS

Sheet Parser
Shared parser for Google Sheets.
"""

from apps.database_engine import (
    get_budget_sheet,
    get_finance_sheet,
    get_guestlist_sheet,
    get_expense_log_sheet,
)
from apps.status_engine import finance_status


def number(value):
    """
    Convert values such as:
    $4,877.50
    4,877.50
    4877.50

    into a float.
    """
    try:
        return float(
            str(value)
            .replace("$", "")
            .replace(",", "")
            .strip()
        )
    except (ValueError, TypeError):
        return 0.0


# ====================================================
# Wedding Budget
# ====================================================

def get_budget_summary():
    rows = get_budget_sheet()

    budget = {
        "total_budget": 0.0,
        "paid": 0.0,
        "balance": 0.0,
        "current_savings": 0.0,
    }

    for row in rows:
        row_text = " ".join(str(cell) for cell in row)

        is_total_row = (
            len(row) >= 4
            and str(row[0]).strip() == ""
            and str(row[1]).strip().startswith("$")
            and str(row[2]).strip().startswith("$")
            and str(row[3]).strip().startswith("$")
        )

        if is_total_row:
            budget["total_budget"] = number(row[1])
            budget["paid"] = number(row[2])
            budget["balance"] = number(row[3])

        if "Current Savings" in row_text and len(row) > 1:
            budget["current_savings"] = number(row[1])

    budget["shortfall"] = (
        budget["balance"] - budget["current_savings"]
    )

    budget["paid_percentage"] = (
        budget["paid"] / budget["total_budget"] * 100
        if budget["total_budget"]
        else 0.0
    )

    return budget


# ====================================================
# Guestlist
# ====================================================

def get_guest_summary():
    rows = get_guestlist_sheet()

    guest = {
        "shaun_total": "-",
        "maria_total": "-",
        "total_guests": "-",
        "seats_available": "-",
        "cards_total": "-",
        "cards_shaun": "-",
        "cards_maria": "-",
        "cards_balance": "-",
    }

    total_counter = 0

    for row in rows:
        for index, cell in enumerate(row):
            value = str(cell).strip()
            next_value = (
                row[index + 1]
                if index + 1 < len(row)
                else "-"
            )

            if value == "Total:":
                total_counter += 1

                if total_counter == 1:
                    guest["shaun_total"] = next_value
                elif total_counter == 2:
                    guest["maria_total"] = next_value

            elif "Total as of" in value:
                guest["total_guests"] = next_value

            elif value == "seats available":
                guest["seats_available"] = next_value

            elif value == "Cards:":
                guest["cards_total"] = next_value

            elif value == "Shaun:":
                guest["cards_shaun"] = next_value

            elif value == "Maria:":
                guest["cards_maria"] = next_value

            elif value == "Balance:":
                guest["cards_balance"] = next_value

    return guest


# ====================================================
# Finance
# ====================================================

def get_finance_summary():
    rows = get_finance_sheet()

    income = 0.0
    savings = 0.0
    bills = 0.0
    insurance = 0.0

    for row in rows:
        if len(row) < 9:
            continue

        category = str(row[1]).strip()
        amount = number(row[4])
        status = str(row[8]).strip().lower()

        if status != "active":
            continue

        match category:
            case "Income":
                income += amount
            case "Savings":
                savings += amount
            case "Bills":
                bills += amount
            case "Insurance":
                insurance += amount

    commitments = savings + bills + insurance
    available = income - commitments
    health = finance_status(available)

    return {
        "salary": income,
        "savings": savings,
        "bills": bills,
        "insurance": insurance,
        "commitments": commitments,
        "available": available,
        "health": health,
    }


# ====================================================
# Bills
# ====================================================

def get_bills_summary():
    rows = get_finance_sheet()

    bills = []
    total = 0.0

    priority_order = {
        "HIGH": 0,
        "MEDIUM": 1,
        "LOW": 2,
    }

    for row in rows:
        if len(row) < 9:
            continue

        category = str(row[1]).strip()
        status = str(row[8]).strip().lower()

        if category != "Bills" or status != "active":
            continue

        amount = number(row[4])
        total += amount

        bills.append(
            {
                "item": str(row[2]).strip(),
                "amount": amount,
                "due": str(row[5]).strip(),
                "priority": str(row[7]).strip().upper(),
            }
        )

    bills.sort(
        key=lambda bill: priority_order.get(
            bill["priority"],
            99,
        )
    )

    return {
        "total": total,
        "bills": bills,
    }


# ====================================================
# Insurance
# ====================================================

def get_insurance_summary():
    rows = get_finance_sheet()

    policies = []
    active_total = 0.0

    for row in rows:
        if len(row) < 9:
            continue

        category = str(row[1]).strip()

        if category != "Insurance":
            continue

        status = str(row[8]).strip()
        is_active = status.lower() == "active"
        amount = number(row[4])

        if is_active:
            active_total += amount

        policies.append(
            {
                "item": str(row[2]).strip(),
                "owner": str(row[3]).strip(),
                "amount": amount,
                "due": str(row[5]).strip(),
                "frequency": str(row[6]).strip(),
                "status": status,
                "is_active": is_active,
            }
        )

    policies.sort(
        key=lambda policy: (
            not policy["is_active"],
            policy["owner"].lower(),
            policy["item"].lower(),
        )
    )

    return {
        "policies": policies,
        "active_total": active_total,
        "active_count": sum(
            1 for policy in policies
            if policy["is_active"]
        ),
        "policy_count": len(policies),
    }
# ====================================================
# Expense Log
# ====================================================

from datetime import datetime


def get_expense_summary():

    rows = get_expense_log_sheet()

    summary = {
        "total": 0.0,
        "count": 0,
        "categories": {},
    }

    current_month = datetime.now().month
    current_year = datetime.now().year

    for row in rows:

        if len(row) < 9:
            continue

        try:
            date = datetime.strptime(
                row[0],
                "%d-%b-%Y",
            )
        except Exception:
            continue

        if (
            date.month != current_month
            or date.year != current_year
        ):
            continue

        category = str(row[3]).strip()
        amount = number(row[5])

        summary["total"] += amount
        summary["count"] += 1

        summary["categories"][category] = (
            summary["categories"].get(category, 0)
            + amount
        )

    return summary