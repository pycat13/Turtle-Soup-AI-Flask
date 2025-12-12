async function login(username, password) {
    const res = await apiFetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) {
        throw new Error(data.error || "login_failed");
    }
    if (data.token) {
        localStorage.setItem("token", data.token);
    }
    return data;
}

async function register(username, password) {
    const res = await apiFetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) {
        throw new Error(data.error || "register_failed");
    }
    return data;
}

function logout() {
    localStorage.removeItem("token");
}

window.AuthApi = { login, register, logout };
