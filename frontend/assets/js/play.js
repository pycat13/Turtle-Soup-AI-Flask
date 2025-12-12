let sessionId = null;
let puzzleId = null;
let mode = null;
let limitSeconds = null;
let limitQuestions = null;
let startTime = null;
let questionUsed = 0;
let timerInterval = null;

function getQueryParam(key) {
    const params = new URLSearchParams(window.location.search);
    return params.get(key);
}

function goBack() {
    history.back();
}

function addMessage(role, text) {
    const area = document.getElementById("chat-area");
    const div = document.createElement("div");
    div.className = "chat-msg " + role;
    div.innerHTML = text;
    area.appendChild(div);
    area.scrollTop = area.scrollHeight;
}

async function loadPuzzle() {
    const titleEl = document.getElementById("puzzle-title");
    const descEl = document.getElementById("puzzle-desc");
    const welcome = document.getElementById("welcome-msg");

    try {
        const res = await apiFetch(`/api/puzzles/${puzzleId}`);
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "puzzle_not_found");
        titleEl.textContent = data.title || "Mystery";
        descEl.textContent = data.description || "No description.";
        welcome.innerHTML = `Welcome!<br>Case: <b>${data.title}</b><br>Situation: "${data.description}"<br><br>Ask Yes/No questions to find the truth!`;
    } catch (err) {
        console.warn(err);
        titleEl.textContent = "Mystery";
        descEl.textContent = "Description unavailable.";
        welcome.textContent = "Ask Yes/No questions to find the truth!";
    }
}

function updateQuestionBox() {
    const box = document.getElementById("question-box");
    if (limitQuestions) {
        const remaining = Math.max(0, limitQuestions - questionUsed);
        box.textContent = `Questions: ${questionUsed} / ${limitQuestions} (left ${remaining})`;
    } else {
        box.textContent = `Questions: ${questionUsed}`;
    }
}

function startCountdown() {
    const box = document.getElementById("timer-box");
    if (!limitSeconds || !startTime) {
        box.textContent = "Time: --";
        return;
    }
    function tick() {
        const now = Date.now();
        const elapsed = Math.floor((now - startTime) / 1000);
        const remaining = Math.max(0, limitSeconds - elapsed);
        const m = String(Math.floor(remaining / 60)).padStart(2, "0");
        const s = String(remaining % 60).padStart(2, "0");
        box.textContent = `Time: ${m}:${s}`;
        if (remaining <= 0 && timerInterval) {
            clearInterval(timerInterval);
            addMessage("system", "<b>System:</b> Time is over.");
        }
    }
    tick();
    timerInterval = setInterval(tick, 1000);
}

async function sendQuestion() {
    const qInput = document.getElementById("question");
    const q = qInput.value.trim();
    if (!q) return;
    if (!sessionId) {
        alert("缺少 session");
        return;
    }

    addMessage("user", "<b>You:</b> " + q);
    qInput.value = "";

    try {
        const res = await apiFetch("/api/play/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId, question: q }),
        });
        const data = await res.json();
        if (res.status === 401) {
            addMessage("system", "<b>System:</b> Please login again.");
            window.location.href = `/login.html?redirect=${encodeURIComponent(window.location.pathname + window.location.search)}`;
            return;
        }
        if (!res.ok) {
            addMessage("system", `<b>System:</b> ${data.error || "error"}`);
            return;
        }
        // 成功算一次提问
        questionUsed += 1;
        updateQuestionBox();

        if (data.type === "guess_result") {
            addMessage("system", `<b>Result:</b> ${data.answer}`);
        } else {
            addMessage("ai", "<b>Answer:</b> " + data.answer);
        }
    } catch (err) {
        console.error(err);
        addMessage("system", "<b>System:</b> Network error");
    }
}

async function finishGame(result) {
    if (!sessionId) {
        alert("缺少 session");
        return;
    }
    try {
        const res = await apiFetch("/api/play/finish", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId, result }),
        });
        const data = await res.json();
        if (res.status === 401) {
            alert("请先登录");
            window.location.href = `/login.html?redirect=${encodeURIComponent(window.location.pathname + window.location.search)}`;
            return;
        }
        const statusText = document.getElementById("status-text");
        if (!res.ok) {
            statusText.textContent = data.error || "finish failed";
            return;
        }
        statusText.textContent = `Finished: ${data.result}, score ${data.score}`;
    } catch (err) {
        console.error(err);
        alert("网络异常");
    }
}

function init() {
    sessionId = getQueryParam("session_id");
    puzzleId = getQueryParam("puzzle_id");
    mode = getQueryParam("mode");
    limitSeconds = parseInt(getQueryParam("limit_seconds"), 10);
    limitSeconds = Number.isFinite(limitSeconds) ? limitSeconds : null;
    limitQuestions = parseInt(getQueryParam("limit_questions"), 10);
    limitQuestions = Number.isFinite(limitQuestions) ? limitQuestions : null;
    const startTimeStr = getQueryParam("start_time");
    startTime = startTimeStr ? Date.parse(startTimeStr) : null;

    if (mode === "timed" && !limitSeconds) {
        limitSeconds = 300; // fallback to 5 minutes
    }
    if (mode === "timed" && !startTime) {
        startTime = Date.now();
    }

    const modeEl = document.getElementById("mode-text");
    if (mode) modeEl.textContent = `${mode.toUpperCase()} MODE`;

    updateQuestionBox();
    startCountdown();
    loadPuzzle();
}

window.addEventListener("DOMContentLoaded", init);
