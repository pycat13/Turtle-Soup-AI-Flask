let currentUser = null;

async function ensureAdmin() {
    const token = getToken();
    if (!token) {
        window.location.href = "/login.html?redirect=" + encodeURIComponent(window.location.pathname);
        return false;
    }
    try {
        const res = await apiFetch("/api/auth/me");
        const data = await res.json();
        if (!res.ok || !data.user || !data.user.is_admin) {
            window.location.href = "/login.html?redirect=" + encodeURIComponent(window.location.pathname);
            return false;
        }
        currentUser = data.user;
        return true;
    } catch (e) {
        window.location.href = "/login.html?redirect=" + encodeURIComponent(window.location.pathname);
        return false;
    }
}

async function loadPuzzles() {
    const body = document.getElementById("puzzle-body");
    body.innerHTML = "<tr><td colspan='7'>Loading...</td></tr>";
    try {
        const res = await apiFetch("/api/admin/puzzles");
        const data = await res.json();
        if (res.status === 401 || res.status === 403) {
            body.innerHTML = "<tr><td colspan='7'>Unauthorized</td></tr>";
            window.location.href = "/login.html?redirect=" + encodeURIComponent(window.location.pathname);
            return;
        }
        const list = data.data || [];
        if (list.length === 0) {
            body.innerHTML = "<tr><td colspan='7'>No puzzles</td></tr>";
            return;
        }
        body.innerHTML = "";
        list.forEach((p) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${p.id}</td>
                <td>${p.title_zh || ""}</td>
                <td>${p.title_en || ""}</td>
                <td>${p.description_zh || ""}</td>
                <td>${p.description_en || ""}</td>
                <td>${p.standard_answer_zh || ""}</td>
                <td>${p.standard_answer_en || ""}</td>
                <td>
                    <button class="btn btn-secondary" onclick="editPuzzle(${p.id})">Edit</button>
                    <button class="btn btn-danger" onclick="deletePuzzle(${p.id})">Delete</button>
                </td>
            `;
            body.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
        body.innerHTML = "<tr><td colspan='7'>Network error</td></tr>";
    }
}

async function loadUsers() {
    const body = document.getElementById("user-body");
    body.innerHTML = "<tr><td colspan='5'>Loading...</td></tr>";
    try {
        const res = await apiFetch("/api/admin/users");
        const data = await res.json();
        if (res.status === 401 || res.status === 403) {
            body.innerHTML = "<tr><td colspan='5'>Unauthorized</td></tr>";
            return;
        }
        const list = data.data || [];
        if (list.length === 0) {
            body.innerHTML = "<tr><td colspan='5'>No users</td></tr>";
            return;
        }
        body.innerHTML = "";
        list.forEach((u) => {
            const isSelf = currentUser && u.id === currentUser.id;
            const isProtected = isSelf || u.username === "admin";
            const toggleText = u.is_admin ? "Revoke" : "Make Admin";
            const toggleClass = u.is_admin ? "btn-danger" : "btn-secondary";
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${u.id}</td>
                <td>${u.username}</td>
                <td>${u.is_admin ? "Yes" : "No"}</td>
                <td>${u.created_at || ""}</td>
                <td>
                    <button class="btn ${toggleClass} ${isProtected ? "btn-muted" : ""}" ${isProtected ? "disabled" : ""} onclick="toggleAdmin(${u.id}, ${u.is_admin ? "false" : "true"})">${toggleText}</button>
                    <button class="btn btn-danger ${isProtected ? "btn-muted" : ""}" ${isProtected ? "disabled" : ""} onclick="deleteUser(${u.id})">Delete</button>
                </td>
            `;
            body.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
        body.innerHTML = "<tr><td colspan='5'>Network error</td></tr>";
    }
}

async function toggleAdmin(userId, isAdmin) {
    try {
        const res = await apiFetch(`/api/admin/users/${userId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ is_admin: isAdmin }),
        });
        const data = await res.json();
        if (!res.ok) {
            alert(data.error || "Update failed");
            return;
        }
        loadUsers();
    } catch (e) {
        console.error(e);
        alert("Network error");
    }
}

async function deleteUser(userId) {
    if (!confirm("Delete this user? This will remove their sessions/scores.")) return;
    try {
        const res = await apiFetch(`/api/admin/users/${userId}`, { method: "DELETE" });
        const data = await res.json();
        if (!res.ok) {
            alert(data.error || "Delete failed");
            return;
        }
        loadUsers();
    } catch (e) {
        console.error(e);
        alert("Network error");
    }
}

async function createPuzzle() {
    const title_zh = document.getElementById("title_zh").value.trim();
    const description_zh = document.getElementById("description_zh").value.trim();
    const standard_answer_zh = document.getElementById("standard_answer_zh").value.trim();
    const title_en = document.getElementById("title_en").value.trim();
    const description_en = document.getElementById("description_en").value.trim();
    const standard_answer_en = document.getElementById("standard_answer_en").value.trim();
    const err = document.getElementById("form-error");
    err.textContent = "";
    if (!title_zh || !description_zh || !standard_answer_zh) {
        err.textContent = "Please fill Chinese fields";
        return;
    }
    try {
        const res = await apiFetch("/api/admin/puzzles", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                title_zh,
                description_zh,
                standard_answer_zh,
                title_en,
                description_en,
                standard_answer_en,
            }),
        });
        const data = await res.json();
        if (!res.ok) {
            err.textContent = data.error || "Create failed";
            return;
        }
        ["title_zh","description_zh","standard_answer_zh","title_en","description_en","standard_answer_en"].forEach((id)=>{ const el=document.getElementById(id); if (el) el.value=""; });
        loadPuzzles();
    } catch (e) {
        console.error(e);
        err.textContent = "Network error";
    }
}

async function editPuzzle(id) {
    const title_zh = prompt("New title (ZH):");
    if (title_zh === null) return;
    const description_zh = prompt("New description (ZH):");
    if (description_zh === null) return;
    const standard_answer_zh = prompt("New standard answer (ZH):");
    if (standard_answer_zh === null) return;
    const title_en = prompt("New title (EN) [optional]:");
    if (title_en === null) return;
    const description_en = prompt("New description (EN) [optional]:");
    if (description_en === null) return;
    const standard_answer_en = prompt("New standard answer (EN) [optional]:");
    if (standard_answer_en === null) return;

    try {
        const res = await apiFetch(`/api/admin/puzzles/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                title_zh,
                description_zh,
                standard_answer_zh,
                title_en,
                description_en,
                standard_answer_en,
            }),
        });
        const data = await res.json();
        if (!res.ok) {
            alert(data.error || "Update failed");
            return;
        }
        loadPuzzles();
    } catch (e) {
        console.error(e);
        alert("Network error");
    }
}

async function deletePuzzle(id) {
    if (!confirm("Delete this puzzle?")) return;
    try {
        const res = await apiFetch(`/api/admin/puzzles/${id}`, { method: "DELETE" });
        const data = await res.json();
        if (!res.ok) {
            alert(data.error || "Delete failed");
            return;
        }
        loadPuzzles();
    } catch (e) {
        console.error(e);
        alert("Network error");
    }
}

window.addEventListener("DOMContentLoaded", async () => {
    const ok = await ensureAdmin();
    if (!ok) return;
    loadPuzzles();
    loadUsers();
});
