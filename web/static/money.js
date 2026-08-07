function formatMoney(value) {
    return new Intl.NumberFormat(
        "en-SG",
        {
            style: "currency",
            currency: "SGD",
        }
    ).format(value);
}


async function loadMoneyPage() {
    try {
        const response = await fetch(
            "/api/money"
        );

        const data =
            await response.json();

        if (!data.success) {
            return;
        }

        document.getElementById(
            "money-page-available"
        ).textContent =
            formatMoney(
                data.available_money
            );

        document.getElementById(
            "money-page-income"
        ).textContent =
            formatMoney(
                data.income
            );

        document.getElementById(
            "money-page-expenses"
        ).textContent =
            formatMoney(
                data.expenses
            );

        document.getElementById(
            "money-page-allocated"
        ).textContent =
            formatMoney(
                data.allocated
            );

        document.getElementById(
            "money-page-cashflow"
        ).textContent =
            formatMoney(
                data.monthly_cash_flow
            );

        document.getElementById(
            "money-page-savings"
        ).textContent =
            formatMoney(
                data.savings
            );

        document.getElementById(
            "money-page-bills"
        ).textContent =
            formatMoney(
                data.bills
            );

        document.getElementById(
            "money-page-insurance"
        ).textContent =
            formatMoney(
                data.insurance
            );

        document.getElementById(
            "money-page-health"
        ).textContent =
            data.health;

    } catch (error) {
        console.error(
            "MoneyOS failed:",
            error
        );
    }
}


document.addEventListener(
    "DOMContentLoaded",
    loadMoneyPage
);