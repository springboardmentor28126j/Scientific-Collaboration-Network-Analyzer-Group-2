import type { ApiError } from "@/types";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export function getHeaders(isFormData = false): HeadersInit {
  const token = localStorage.getItem("access_token");
  const headers: HeadersInit = {};
  if (!isFormData) {
    headers["Content-Type"] = "application/json";
  }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

export async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = (await response.json().catch(() => ({}))) as ApiError | { detail?: string };
    const message =
      (errorData as ApiError).detail?.[0]?.msg ||
      (errorData as { detail?: string }).detail ||
      `HTTP ${response.status}: ${response.statusText}`;
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}
