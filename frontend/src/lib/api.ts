/**
 * Centralized API client for talking to the FastAPI backend.
 *
 * All backend calls go through here, giving one place to configure the
 * base URL, headers, and error handling.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Perform a GET request against the backend.
 */
export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`);
  if (!res.ok) {
    throw new Error(`GET ${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

/**
 * Perform a POST request against the backend.
 */
export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`POST ${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}