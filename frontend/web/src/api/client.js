// Shared fetch wrapper. Every API file goes through this so the base URL,
// headers and error handling live in one place.
//
// '/api' is forwarded to the FastAPI backend by the proxy in vite.config.js.
const BASE_URL = '/api';

export async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  // fetch only rejects on network failure, so HTTP errors (404, 500...) must be checked by hand.
  if (!res.ok) {
    // FastAPI puts its error message in { "detail": ... }; fall back to the status text.
    const body = await res.json().catch(() => null);
    const detail = typeof body?.detail === 'string' ? body.detail : null;
    throw new Error(detail ?? `Request failed: ${res.status} ${res.statusText}`);
  }

  // 204 No Content has no body to parse.
  return res.status === 204 ? null : res.json();
}
