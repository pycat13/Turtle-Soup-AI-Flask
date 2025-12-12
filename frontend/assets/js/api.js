// Basic API helper; attaches Authorization header if token exists
function getToken() {
    return localStorage.getItem("token");
}

async function apiFetch(url, options = {}) {
    const headers = options.headers || {};
    const token = getToken();
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    return fetch(url, {
        ...options,
        headers,
    });
}

window.apiFetch = apiFetch;
window.getToken = getToken;
