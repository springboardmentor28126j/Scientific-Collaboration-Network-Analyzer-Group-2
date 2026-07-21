import { API_BASE_URL, getHeaders, handleResponse } from "./core";
import type { TokenPair, UserMe, MessageResponse } from "@/types";

export async function login(username: string, password: string): Promise<TokenPair> {
  const formData = new URLSearchParams();
  formData.append("grant_type", "password");
  formData.append("username", username);
  formData.append("password", password);

  const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData,
  });
  return handleResponse<TokenPair>(response);
}

export async function refreshToken(refresh_token: string): Promise<TokenPair> {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token }),
  });
  return handleResponse<TokenPair>(response);
}

export async function getMe(): Promise<UserMe> {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
    headers: getHeaders(),
  });
  return handleResponse<UserMe>(response);
}

export async function verifyEmail(token: string): Promise<MessageResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/verify-email`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token }),
  });
  return handleResponse<MessageResponse>(response);
}

export async function verifyInvite(token: string, password: string): Promise<MessageResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/verify-invite`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, password }),
  });
  return handleResponse<MessageResponse>(response);
}

export async function forgotPassword(email: string): Promise<MessageResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/forgot-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  return handleResponse<MessageResponse>(response);
}

export async function resetPassword(token: string, new_password: string): Promise<MessageResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/reset-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, new_password }),
  });
  return handleResponse<MessageResponse>(response);
}
