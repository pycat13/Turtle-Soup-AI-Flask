async function loadPuzzles() {
    const grid = document.getElementById("puzzle-grid");
    const t = (key, fallback) => (window.I18N ? I18N.t(key, fallback) : fallback);
    grid.innerHTML = `<div class='riddle-card card-yellow'><h2 class='card-title'>${t("common.loading", "Loading...")}</h2></div>`;

    try {
        const lang = (window.I18N && I18N.getLang && I18N.getLang()) || "zh";
        const res = await fetch(`/api/puzzles?lang=${encodeURIComponent(lang)}`);
        const data = await res.json();
        if (!res.ok) {
            grid.innerHTML = `<div class='riddle-card card-yellow'><h2 class='card-title'>${t("common.failedToLoad", "Failed to load")}</h2></div>`;
            return;
        }

        if (!Array.isArray(data) || data.length === 0) {
            grid.innerHTML = `<div class='riddle-card card-yellow'><h2 class='card-title'>${t("common.noData", "No puzzles yet")}</h2></div>`;
            return;
        }

        grid.innerHTML = "";
        data.forEach((puzzle, idx) => {
            const card = document.createElement("a");
            card.className = "riddle-card " + (idx % 2 === 0 ? "card-green" : "card-yellow");
            card.href = `/play_mode.html?puzzle_id=${puzzle.id}`;

            card.innerHTML = `
                <span class="badge">${t("common.puzzle", "PUZZLE")}</span>
                <h2 class="card-title">${puzzle.title || "Untitled"}</h2>
                <p class="card-desc">${puzzle.description || ""}</p>
                <div class="play-row">${t("common.playNow", "Play Now ->")}</div>
            `;
            grid.appendChild(card);
        });
    } catch (err) {
        console.error(err);
        grid.innerHTML = `<div class='riddle-card card-yellow'><h2 class='card-title'>${t("common.networkError", "Network error")}</h2></div>`;
    }
}

window.addEventListener("DOMContentLoaded", loadPuzzles);
