const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const detail = data.detail?.message || data.detail?.code || data.error?.message;
    throw new Error(detail || "Request failed.");
  }

  return data;
}

export const api = {
  health: () => request("/api/health"),
  mcpStatus: () => request("/api/mcp/status"),
  mcpTools: () => request("/api/mcp/tools"),
  chat: (message) =>
    request("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    }),
};
