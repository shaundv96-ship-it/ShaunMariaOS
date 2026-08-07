function formatMoney(value) {
    return new Intl.NumberFormat(
        "en-SG",
        {
            style: "currency",
            currency: "SGD",
        }
    ).format(value);
}


async function loadMoney() {
    try {
        const response = await fetch(
            "/api/money"
        );

        const data = await response.json();

        if (!data.success) {
            console.error(
                "MoneyOS returned an unsuccessful response."
            );
            return;
        }

        document.getElementById(
            "available-money"
        ).textContent = formatMoney(
            data.available_money
        );

        document.getElementById(
            "income"
        ).textContent = formatMoney(
            data.income
        );

        document.getElementById(
            "expenses"
        ).textContent = formatMoney(
            data.expenses
        );

        document.getElementById(
            "allocated"
        ).textContent = formatMoney(
            data.allocated
        );

        document.getElementById(
            "money-health"
        ).textContent = data.health;

    } catch (error) {
        console.error(
            "MoneyOS failed to load:",
            error
        );
    }
}


function loadWeddingCountdown() {
    const weddingDate = new Date(
        "2026-10-31T00:00:00+08:00"
    );

    const now = new Date();

    const difference =
        weddingDate.getTime()
        - now.getTime();

    const days = Math.max(
        0,
        Math.ceil(
            difference
            / (1000 * 60 * 60 * 24)
        )
    );

    document.getElementById(
        "wedding-countdown"
    ).textContent =
        `${days} days to go`;
}


async function loadTodayCalendar() {
    const container =
        document.getElementById(
            "today-events"
        );

    if (!container) {
        return;
    }

    try {
        const response = await fetch(
            "/api/calendar/today"
        );

        const data =
            await response.json();

        container.innerHTML = "";

        if (!data.success) {
            container.innerHTML = `
                <article class="card schedule-card">
                    <div>
                        <strong>
                            Calendar unavailable
                        </strong>
                        <p>
                            Please try again shortly.
                        </p>
                    </div>
                </article>
            `;
            return;
        }

        if (!data.events.length) {
            container.innerHTML = `
                <article class="card schedule-card empty-schedule">
                    <div class="schedule-time">
                        ✨
                    </div>

                    <div>
                        <strong>
                            Nothing planned today
                        </strong>

                        <p>
                            Your calendar is clear.
                        </p>
                    </div>
                </article>
            `;
            return;
        }

        data.events.forEach(
            event => {
                container.appendChild(
                    buildEventCard(event)
                );
            }
        );

    } catch (error) {
        console.error(
            "CalendarOS failed to load:",
            error
        );
    }
}


document.addEventListener(
    "DOMContentLoaded",
    () => {
        loadMoney();
        loadWeddingCountdown();
        loadTodayCalendar();
    }
);