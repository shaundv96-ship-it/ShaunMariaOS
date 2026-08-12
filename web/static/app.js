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

async function loadTasksSummary() {
    try {
        const response = await fetch(
            "/api/tasks"
        );

        const data = await response.json();

        const countElement =
            document.getElementById(
                "home-task-count"
            );

        const messageElement =
            document.getElementById(
                "home-task-message"
            );

        if (!data.success) {
            countElement.textContent = "—";
            messageElement.textContent =
                "TasksOS unavailable.";
            return;
        }

        const count =
            data.count ?? 0;

        countElement.textContent =
            `${count} remaining`;

        if (count === 0) {
            messageElement.textContent =
                "You're all caught up. ✨";
        } else if (count === 1) {
            messageElement.textContent =
                "Just one thing left.";
        } else if (count <= 3) {
            messageElement.textContent =
                "You're on track.";
        } else {
            messageElement.textContent =
                "A few things need attention.";
        }

    } catch (error) {
        console.error(
            "TasksOS summary failed:",
            error
        );
    }
}

async function loadWeddingProgress() {
    const progressFill =
        document.getElementById(
            "wedding-progress-fill"
        );

    if (!progressFill) {
        return;
    }

    try {
        const response = await fetch(
            "/api/us/overview"
        );

        const data =
            await response.json();

        const weddingFund =
            data.wedding_fund;

        if (
            !data.success ||
            !weddingFund
        ) {
            return;
        }

        const paidPercentage =
            Number(
                weddingFund.paid_percentage
            ) || 0;

        const safePercentage =
            Math.min(
                100,
                Math.max(
                    0,
                    paidPercentage
                )
            );

        progressFill.style.width =
            `${safePercentage}%`;

    } catch (error) {
        console.error(
            "Wedding progress failed to load:",
            error
        );
    }
}

async function loadAdvisor() {
    const titleElement =
        document.getElementById(
            "advisor-title"
        );

    const messageElement =
        document.getElementById(
            "advisor-message"
        );

    if (!titleElement || !messageElement) {
        return;
    }

    try {
        const response = await fetch(
            "/api/advisor"
        );

        const data =
            await response.json();

        if (!data.success) {
            titleElement.textContent =
                "Advisor unavailable.";

            messageElement.textContent =
                data.message ||
                "Please try again shortly.";

            return;
        }

        titleElement.textContent =
            data.title;

        messageElement.textContent =
            data.message;

    } catch (error) {
        console.error(
            "Advisor failed to load:",
            error
        );

        titleElement.textContent =
            "Advisor unavailable.";

        messageElement.textContent =
            "Please try again shortly.";
    }
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function formatCalendarMoment(value) {
    if (!value) {
        return "";
    }

    const parsed = new Date(value);

    if (Number.isNaN(parsed.getTime())) {
        return String(value);
    }

    return new Intl.DateTimeFormat(
        "en-SG",
        {
            weekday: "short",
            day: "numeric",
            month: "short",
            hour: "numeric",
            minute: "2-digit",
        }
    ).format(parsed);
}


function getCommandSummary(
    data,
    originalText
) {
    const details =
        data.data || {};

    if (data.intent === "expense") {
        const item =
            details.item ||
            "Expense";

        const amount =
            typeof details.amount === "number"
                ? formatMoney(details.amount)
                : null;

        const category =
            details.category || null;

        return [
            item,
            amount,
            category,
        ]
            .filter(Boolean)
            .join(" · ");
    }


    if (data.intent === "income") {
        const item =
            details.item ||
            "Income";

        const amountValue =
            details.amount ??
            details.value;

        const amount =
            typeof amountValue === "number"
                ? formatMoney(amountValue)
                : null;

        return [
            item,
            amount,
        ]
            .filter(Boolean)
            .join(" · ");
    }


    if (data.intent === "task") {
    const task =
        details.task || {};

    const title =
        task.title ||
        task.item ||
        task.task ||
        originalText;

    const dueDate =
        task.due_date || "";

    if (!dueDate) {
        return title;
    }

    const parsedDueDate =
        new Date(dueDate);

    let formattedDueDate =
        dueDate;

    if (
        !Number.isNaN(
            parsedDueDate.getTime()
        )
    ) {
        formattedDueDate =
            parsedDueDate.toLocaleDateString(
                "en-SG",
                {
                    day: "numeric",
                    month: "short",
                }
            );
    }

    return (
        `${title} · Due ${formattedDueDate}`
    );
}


    if (data.intent === "calendar") {
    const event =
        details.parsed_event || {};

    const title =
        event.title ||
        "Calendar event";

    if (event.all_day) {
        const startDate =
            event.start_date;

        const endDate =
            event.end_date;

        if (
            startDate &&
            endDate
        ) {
            const start =
                new Date(
                    `${startDate}T00:00:00+08:00`
                );

            const end =
                new Date(
                    `${endDate}T00:00:00+08:00`
                );

            const sameDay =
                startDate === endDate;

            const startDay =
                start.toLocaleDateString(
                    "en-SG",
                    {
                        day: "numeric",
                    }
                );

            const endDay =
                end.toLocaleDateString(
                    "en-SG",
                    {
                        day: "numeric",
                    }
                );

            const startMonth =
                start.toLocaleDateString(
                    "en-SG",
                    {
                        month: "short",
                    }
                );

            const endMonth =
                end.toLocaleDateString(
                    "en-SG",
                    {
                        month: "short",
                    }
                );

            let dateLabel;

            if (sameDay) {
                dateLabel =
                    `${startDay} ${startMonth}`;
            } else if (
                startMonth === endMonth
            ) {
                dateLabel =
                    `${startDay}–${endDay} ${startMonth}`;
            } else {
                dateLabel =
                    `${startDay} ${startMonth}–${endDay} ${endMonth}`;
            }

            return (
                `${title} · ${dateLabel} · All day`
            );
        }

        return (
            `${title} · All day`
        );
    }

    const start =
        event.start_time;

    const formattedStart =
        start
            ? formatCalendarMoment(start)
            : "";

    return [
        title,
        formattedStart,
    ]
        .filter(Boolean)
        .join(" · ");
}

    return originalText;
}

async function runGlobalCommand() {
    const input =
        document.getElementById(
            "global-command-input"
        );

    const button =
        document.getElementById(
            "global-command-button"
        );

    const resultBox =
        document.getElementById(
            "global-command-result"
        );

    if (!input || !button || !resultBox) {
        return;
    }

    const text =
        input.value.trim();

    if (!text) {
        resultBox.innerHTML = `
            <p class="quick-add-error">
                Tell me what you'd like to do.
            </p>
        `;

        return;
    }

    button.disabled = true;
    input.disabled = true;
    button.textContent = "…";

    try {
        const response = await fetch(
            "/api/command",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",
                },

                body: JSON.stringify({
                    text: text,
                }),
            }
        );

        const data =
            await response.json();

        if (!data.success) {
            resultBox.innerHTML = `
                <p class="quick-add-error">
                    ${escapeHtml(data.message)}
                </p>
            `;

            return;
        }

        const labels = {
            calendar: "Added to Calendar",
            task: "Task added",
            expense: "Expense recorded",
            income: "Income updated",
        };

        const label =
            labels[data.intent]
            || "Done";

        const summary =
            getCommandSummary(
                data,
                text
            );

        resultBox.innerHTML = `
            <div class="quick-add-success">

                <strong>
                    ✓ ${escapeHtml(label)}
                </strong>

                <span>
                    ${escapeHtml(summary)}
                </span>

            </div>
        `;

        input.value = "";

        /*
         * Refresh live Home modules.
         */
        loadTodayCalendar();
        loadTasksSummary();
        loadMoney();
        loadAdvisor();

    } catch (error) {
        console.error(
            "Global command failed:",
            error
        );

        resultBox.innerHTML = `
            <p class="quick-add-error">
                Something went wrong.
            </p>
        `;

    } finally {
        button.disabled = false;
        input.disabled = false;
        button.textContent = "→";
        input.focus();
    }
}

document.addEventListener(
    "DOMContentLoaded",
    () => {
        loadMoney();
        loadWeddingCountdown();
        loadTodayCalendar();
        loadTasksSummary();
        loadAdvisor();
        loadWeddingProgress();
        const commandButton =
    document.getElementById(
        "global-command-button"
    );

const commandInput =
    document.getElementById(
        "global-command-input"
    );

if (commandButton) {
    commandButton.addEventListener(
        "click",
        runGlobalCommand
    );
}

if (commandInput) {
    commandInput.addEventListener(
        "keydown",
        event => {
            if (event.key === "Enter") {
                runGlobalCommand();
            }
        }
    );
}
    }
);

