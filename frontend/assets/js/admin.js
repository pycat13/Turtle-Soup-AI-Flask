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
        return true;
    } catch (e) {
        window.location.href = "/login.html?redirect=" + encodeURIComponent(window.location.pathname);
        return false;
    }
}

async function loadPuzzles() {
    const body = document.getElementById("puzzle-body");
    body.innerHTML = "<tr><td colspan='5'>Loading...</td></tr>";
    try {
        const res = await apiFetch("/api/admin/puzzles");
        const data = await res.json();
        if (res.status === 401 || res.status === 403) {
            body.innerHTML = "<tr><td colspan='5'>Unauthorized</td></tr>";
            window.location.href = "/login.html?redirect=" + encodeURIComponent(window.location.pathname);
            return;
        }
        const list = data.data || [];
        if (list.length === 0) {
            body.innerHTML = "<tr><td colspan='5'>No puzzles</td></tr>";
            return;
        }
        body.innerHTML = "";
        list.forEach((p) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${p.id}</td>
                <td>${p.title}</td>
                <td>${p.description}</td>
                <td>${p.standard_answer || ""}</td>
                <td>
                    <button class="btn btn-secondary" onclick="editPuzzle(${p.id})">Edit</button>
                    <button class="btn btn-danger" onclick="deletePuzzle(${p.id})">Delete</button>
                </td>
            `;
            body.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
        body.innerHTML = "<tr><td colspan='5'>Network error</td></tr>";
    }
}

async function loadUsers() {
    const body = document.getElementById("user-body");
    body.innerHTML = "<tr><td colspan='4'>Loading...</td></tr>";
    try {
        const res = await apiFetch("/api/admin/users");
        const data = await res.json();
        if (res.status === 401 || res.status === 403) {
            body.innerHTML = "<tr><td colspan='4'>Unauthorized</td></tr>";
            return;
        }
        const list = data.data || [];
        if (list.length === 0) {
            body.innerHTML = "<tr><td colspan='4'>No users</td></tr>";
            return;
        }
        body.innerHTML = "";
        list.forEach((u) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${u.id}</td>
                <td>${u.username}</td>
                <td>${u.is_admin ? "Yes" : "No"}</td>
                <td>${u.created_at || ""}</td>
            `;
            body.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
        body.innerHTML = "<tr><td colspan='4'>Network error</td></tr>";
    }
}

async function createPuzzle() {
    const title = document.getElementById("title").value.trim();
    const description = document.getElementById("description").value.trim();
    const standard_answer = document.getElementById("standard_answer").value.trim();
    const err = document.getElementById("form-error");
    err.textContent = "";
    if (!title || !description || !standard_answer) {
        err.textContent = "Please fill all fields";
        return;
    }
    try {
        const res = await apiFetch("/api/admin/puzzles", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, description, standard_answer }),
        });
        const data = await res.json();
        if (!res.ok) {
            err.textContent = data.error || "Create failed";
            return;
        }
        document.getElementById("title").value = "";
        document.getElementById("description").value = "";
        document.getElementById("standard_answer").value = "";
        loadPuzzles();
    } catch (e) {
        console.error(e);
        err.textContent = "Network error";
    }
}

async function editPuzzle(id) {
    const title = prompt("New title:");
    if (title === null) return;
    const description = prompt("New description:");
    if (description === null) return;
    const standard_answer = prompt("New standard answer:");
    if (standard_answer === null) return;

    try {
        const res = await apiFetch(`/api/admin/puzzles/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, description, standard_answer }),
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
