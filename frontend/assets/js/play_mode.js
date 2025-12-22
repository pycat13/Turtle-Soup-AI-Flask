// Mode selection
document.querySelectorAll(".mode-option").forEach((opt) => {
  opt.addEventListener("click", () => {
    document
      .querySelectorAll(".mode-option")
      .forEach((o) => o.classList.remove("selected"));
    opt.classList.add("selected");
  });
});

function getQueryParam(key) {
  const params = new URLSearchParams(window.location.search);
  return params.get(key);
}

async function startGame() {
  const t = (key, fallback) => (window.I18N ? I18N.t(key, fallback) : fallback);

  const selected = document.querySelector(".mode-option.selected");
  const mode = selected.dataset.mode;

  const puzzleId = getQueryParam("puzzle_id");
  if (!puzzleId) {
    alert(t("play_mode.missingPuzzleId", "Missing puzzle id"));
    return;
  }

  try {
    const res = await apiFetch("/api/play/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ puzzle_id: Number(puzzleId), mode }),
    });
    const data = await res.json();

    if (res.status === 401) {
      alert(t("play_mode.pleaseLogin", "Please login"));
      window.location.href = "/login.html";
      return;
    }

    if (!res.ok) {
      alert(data.error || t("common.failedToLoad", "Failed to start"));
      return;
    }

    const {
      session_id,
      puzzle_id,
      mode: serverMode,
      limit_seconds,
      limit_questions,
      start_time,
    } = data;

    const url = `/play.html?session_id=${encodeURIComponent(
      session_id
    )}&puzzle_id=${encodeURIComponent(puzzle_id)}&mode=${encodeURIComponent(
      serverMode
    )}&limit_seconds=${encodeURIComponent(
      limit_seconds || ""
    )}&limit_questions=${encodeURIComponent(
      limit_questions || ""
    )}&start_time=${encodeURIComponent(start_time || "")}`;

    window.location.href = url;
  } catch (err) {
    console.error(err);
    alert(t("common.networkError", "Network error"));
  }
}

window.startGame = startGame;

