export async function apiFetch(url, options = {}) {
  const token = localStorage.getItem("token");

  const headers = {
    ...(options.headers || {}),
    Authorization: token ? `Bearer ${token}` : "",
  };

  const res = await fetch(url, { ...options, headers });

  if (res.status === 401) {
    // Token invalid — clear session
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "/"; // reload React app to show login
    throw new Error("Unauthorized");
  }

  return res;
}