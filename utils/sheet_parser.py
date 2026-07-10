"""
ShaunMariaOS

Sheet Parser
Shared parser for Google Sheets.
"""

from apps.database_engine import (
    get_budget_sheet,
    get_guestlist_sheet,
)
from apps.status_engine import finance_status

def number(value):
    """
    Converts:
    $4,877.50
    4,877.50
    4877.50

    into float.
    """
    try:
        return float(str(value).replace("$", "").replace(",", "").strip())
    except (ValueError, TypeError):
        return 0


# ----------------------------------------------------
# Wedding Budget
# ----------------------------------------------------

def get_budget_summary():
    rows = get_budget_sheet()

    budget = {
        "total_budget": 0,
        "paid": 0,
        "balance": 0,
        "current_savings": 0,
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

        if "Current Savings" in row_text:
            budget["current_savings"] = number(row[1])

    budget["shortfall"] = (
        budget["balance"] - budget["current_savings"]
    )

    budget["paid_percentage"] = (
        budget["paid"] / budget["total_budget"] * 100
        if budget["total_budget"]
        else 0
    )

    return budget


# ----------------------------------------------------
# Guestlist
# ----------------------------------------------------

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

    counter = 0

    for row in rows:

        for i, cell in enumerate(row):

            value = str(cell).strip()

            next_value = row[i + 1] if i + 1 < len(row) else "-"

            if value == "Total:":
                counter += 1

                if counter == 1:
                    guest["shaun_total"] = next_value

                elif counter == 2:
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

from apps.database_engine import get_finance_sheet


def get_finance_summary():
    rows = get_finance_sheet()

    income = 0
    savings = 0
    bills = 0
    insurance = 0

    for row in rows:
        if len(row) < 9:
            continue

        category = str(row[1]).strip()
        amount = row[4]
        status = str(row[8]).strip().lower()

        if status != "active":
            continue

        try:
            value = float(str(amount).replace("$", "").replace(",", ""))
        except (ValueError, TypeError):
            continue

        match category:
            case "Income":
                income += value
            case "Savings":
                savings += value
            case "Bills":
                bills += value
            case "Insurance":
                insurance += value

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

    def get_bills_summary():
    rows = get_finance_sheet()

    bills = []
    total = 0

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

        try:
            amount = number(row[4])
        except Exception:
            continue

        total += amount

        bills.append({
            "item": str(row[2]).strip(),
            "amount": amount,
            "due": str(row[5]).strip(),
            "priority": str(row[7]).strip().upper(),
        })

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

def get_insurance_summary():
    rows = get_finance_sheet()

    policies = []
    active_total = 0

    for row in rows:
        if len(row) < 9:
            continue

        category = str(row[1]).strip()

        if category != "Insurance":
            continue

        item = str(row[2]).strip()
        owner = str(row[3]).strip()
        amount = number(row[4])
        due = str(row[5]).strip()
        frequency = str(row[6]).strip()
        status = str(row[8]).strip()

        is_active = status.lower() == "active"

        if is_active:
            active_total += amount

        policies.append(
            {
                "item": item,
                "owner": owner,
                "amount": amount,
                "due": due,
                "frequency": frequency,
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
            policy["is_active"] for policy in policies
        ),
        "policy_count": len(policies),
    }