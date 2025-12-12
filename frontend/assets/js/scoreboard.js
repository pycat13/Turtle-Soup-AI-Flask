async function loadScores() {
    const tbody = document.getElementById("score-body");
    tbody.innerHTML = "<tr><td colspan='5'>Loading...</td></tr>";
    try {
        const res = await fetch("/api/scores");
        const data = await res.json();
        if (!res.ok) {
            tbody.innerHTML = `<tr><td colspan='5'>Failed: ${data.error || "error"}</td></tr>`;
            return;
        }
        const list = data.data || [];
        if (list.length === 0) {
            tbody.innerHTML = "<tr><td colspan='5'>No scores yet.</td></tr>";
            return;
        }
        tbody.innerHTML = "";
        list.forEach((item, idx) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${idx + 1}</td>
                <td>${item.username || "Unknown"}</td>
                <td class="puzzle">${item.puzzle_title || ("Puzzle #" + item.puzzle_id)}</td>
                <td class="score">${item.score}</td>
                <td class="time">${item.created_at || ""}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
        tbody.innerHTML = "<tr><td colspan='5'>Network error</td></tr>";
    }
}

window.addEventListener("DOMContentLoaded", loadScores);
