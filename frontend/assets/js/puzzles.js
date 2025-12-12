async function loadPuzzles() {
    const grid = document.getElementById("puzzle-grid");
    grid.innerHTML = "<div class='riddle-card card-yellow'><h2 class='card-title'>Loading...</h2></div>";

    try {
        const res = await fetch("/api/puzzles");
        const data = await res.json();
        if (!res.ok) {
            grid.innerHTML = "<div class='riddle-card card-yellow'><h2 class='card-title'>Failed to load</h2></div>";
            return;
        }

        if (!Array.isArray(data) || data.length === 0) {
            grid.innerHTML = "<div class='riddle-card card-yellow'><h2 class='card-title'>No puzzles yet</h2></div>";
            return;
        }

        grid.innerHTML = "";
        data.forEach((puzzle, idx) => {
            const card = document.createElement("a");
            card.className = "riddle-card " + (idx % 2 === 0 ? "card-green" : "card-yellow");
            card.href = `/play_mode.html?puzzle_id=${puzzle.id}`;

            card.innerHTML = `
                <span class="badge">PUZZLE</span>
                <h2 class="card-title">${puzzle.title || "Untitled"}</h2>
                <p class="card-desc">${puzzle.description || ""}</p>
                <div class="play-row">Play Now -></div>
            `;
            grid.appendChild(card);
        });
    } catch (err) {
        console.error(err);
        grid.innerHTML = "<div class='riddle-card card-yellow'><h2 class='card-title'>Network error</h2></div>";
    }
}

window.addEventListener("DOMContentLoaded", loadPuzzles);
