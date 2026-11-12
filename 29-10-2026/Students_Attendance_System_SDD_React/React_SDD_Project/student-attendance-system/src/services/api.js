const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

export async function apiRequest(endpoint, options = {}) {
  const token = sessionStorage.getItem("access_token");

  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.detail || `Request failed with status ${response.status}`
    );
  }

  return data;
}

export async function loginUser(username, password) {
  const data = await apiRequest("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });

  sessionStorage.setItem("access_token", data.access_token);
  return data.user;
}

export async function getCurrentUser() {
  return apiRequest("/auth/me");
}

export async function logoutUser() {
  try {
    await apiRequest("/auth/logout", { method: "POST" });
  } finally {
    sessionStorage.removeItem("access_token");
  }
}