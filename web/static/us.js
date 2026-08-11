function formatMoney(value) {
    return new Intl.NumberFormat(
        "en-SG",
        {
            style: "currency",
            currency: "SGD",
        }
    ).format(value);
}


/* ==========================================================
   Next Chapter
   ========================================================== */

async function loadNextChapter() {
    const icon =
        document.getElementById(
            "chapter-icon"
        );

    const title =
        document.getElementById(
            "chapter-title"
        );

    const subtitle =
        document.getElementById(
            "chapter-subtitle"
        );

    if (!icon || !title || !subtitle) {
        return;
    }

    try {
        const response = await fetch(
            "/api/us/next-chapter"
        );

        if (!response.ok) {
            throw new Error(
                "Could not load next chapter."
            );
        }

        const data =
            await response.json();

        if (!data.success) {
            throw new Error(
                data.message ||
                "Could not load next chapter."
            );
        }

        icon.textContent =
            data.icon;

        title.textContent =
            data.title;

        subtitle.textContent =
            data.subtitle;

    } catch (error) {
        console.error(
            "Next chapter failed to load:",
            error
        );

        icon.textContent = "❤️";

        title.textContent =
            "Our next chapter";

        subtitle.textContent =
            "Something good is coming.";
    }
}


/* ==========================================================
   Wedding Fund
   ========================================================== */

function loadWeddingFund(weddingFund) {
    const card =
        document.getElementById(
            "wedding-fund-card"
        );

    if (!card) {
        return;
    }

    if (!weddingFund) {
        card.hidden = true;
        return;
    }

    card.hidden = false;

    const savings =
        document.getElementById(
            "wedding-fund-savings"
        );

    const balance =
        document.getElementById(
            "wedding-fund-balance"
        );

    const shortfall =
        document.getElementById(
            "wedding-fund-shortfall"
        );

    const percentage =
        document.getElementById(
            "wedding-fund-percentage"
        );

    const progressFill =
        document.getElementById(
            "wedding-fund-progress-fill"
        );

    if (savings) {
        savings.textContent =
            formatMoney(
                weddingFund.current_savings
            );
    }

    if (balance) {
        balance.textContent =
            formatMoney(
                weddingFund.balance
            );
    }

    if (shortfall) {
        shortfall.textContent =
            formatMoney(
                weddingFund.shortfall
            );
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

    if (percentage) {
        percentage.textContent =
            `${safePercentage.toFixed(1)}%`;
    }

    if (progressFill) {
        progressFill.style.width =
            `${safePercentage}%`;
    }
}


/* ==========================================================
   Goal Cards
   ========================================================== */

function buildGoalCard(goal) {
    const article =
        document.createElement(
            "article"
        );

    article.className =
        "card us-goal-card";

    article.innerHTML = `
        <span class="goal-icon">
            ${goal.icon}
        </span>

        <div>
            <span class="card-label">
                ${goal.label}
            </span>

            <strong>
                ${goal.title}
            </strong>

            <p>
                ${goal.subtitle}
            </p>
        </div>
    `;

    return article;
}


/* ==========================================================
   Timeline Cards
   ========================================================== */

function buildTimelineCard(item) {
    const article =
        document.createElement(
            "article"
        );

    article.className =
        "card timeline-card";

    article.innerHTML = `
        <span>
            ${item.icon}
        </span>

        <div>
            <strong>
                ${item.title}
            </strong>

            <p>
                ${item.subtitle}
            </p>
        </div>
    `;

    return article;
}


/* ==========================================================
   Us Overview
   ========================================================== */

async function loadUsOverview() {
    const goalsContainer =
        document.getElementById(
            "us-goals"
        );

    const timelineContainer =
        document.getElementById(
            "us-timeline"
        );

    if (
        !goalsContainer ||
        !timelineContainer
    ) {
        return;
    }

    try {
        const response = await fetch(
            "/api/us/overview"
        );

        if (!response.ok) {
            throw new Error(
                "Could not load Us overview."
            );
        }

        const data =
            await response.json();

        if (!data.success) {
            throw new Error(
                data.message ||
                "Could not load Us overview."
            );
        }

        loadWeddingFund(
            data.wedding_fund
        );

        goalsContainer.innerHTML = "";
        timelineContainer.innerHTML = "";

        data.goals.forEach(
            goal => {
                goalsContainer.appendChild(
                    buildGoalCard(goal)
                );
            }
        );

        data.timeline.forEach(
            item => {
                timelineContainer.appendChild(
                    buildTimelineCard(item)
                );
            }
        );

    } catch (error) {
        console.error(
            "Us overview failed to load:",
            error
        );

        const weddingCard =
            document.getElementById(
                "wedding-fund-card"
            );

        if (weddingCard) {
            weddingCard.hidden = true;
        }

        goalsContainer.innerHTML = `
            <article class="card us-goal-card">
                <span class="goal-icon">
                    ❤️
                </span>

                <div>
                    <span class="card-label">
                        US
                    </span>

                    <strong>
                        Goals unavailable
                    </strong>

                    <p>
                        Please try again shortly.
                    </p>
                </div>
            </article>
        `;

        timelineContainer.innerHTML = `
            <article class="card timeline-card">
                <span>
                    ✨
                </span>

                <div>
                    <strong>
                        Timeline unavailable
                    </strong>

                    <p>
                        Please try again shortly.
                    </p>
                </div>
            </article>
        `;
    }
}


/* ==========================================================
   Page Startup
   ========================================================== */

document.addEventListener(
    "DOMContentLoaded",
    () => {
        loadNextChapter();
        loadUsOverview();
    }
);