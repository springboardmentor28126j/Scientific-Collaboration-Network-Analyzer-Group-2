import { API_BASE_URL, getHeaders, handleResponse } from "./core";
import type { InstitutionUser, Researcher } from "@/types";

export async function createInstitutionUser(data: {
  email: string;
  full_name: string;
  role: "RESEARCHER" | "REVIEWER";
  description?: string;
}): Promise<InstitutionUser> {
  const response = await fetch(`${API_BASE_URL}/api/v1/institution/users`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<InstitutionUser>(response);
}

export async function listInstitutionUsers(role?: "RESEARCHER" | "REVIEWER"): Promise<InstitutionUser[]> {
  const url = new URL(`${API_BASE_URL}/api/v1/institution/users`);
  if (role) url.searchParams.append("role", role);

  const response = await fetch(url.toString(), {
    headers: getHeaders(),
  });
  return handleResponse<InstitutionUser[]>(response);
}

export async function activateUser(user_id: string): Promise<InstitutionUser> {
  const response = await fetch(`${API_BASE_URL}/api/v1/institution/users/${user_id}/activate`, {
    method: "PATCH",
    headers: getHeaders(),
  });
  return handleResponse<InstitutionUser>(response);
}

export async function deactivateUser(user_id: string): Promise<InstitutionUser> {
  const response = await fetch(`${API_BASE_URL}/api/v1/institution/users/${user_id}/deactivate`, {
    method: "PATCH",
    headers: getHeaders(),
  });
  return handleResponse<InstitutionUser>(response);
}

export async function listResearchers(search?: string): Promise<Researcher[]> {
  const url = new URL(`${API_BASE_URL}/api/v1/users/researchers`);
  if (search) {
    url.searchParams.append("search", search);
  }
  const response = await fetch(url.toString(), {
    headers: getHeaders(),
  });
  return handleResponse<Researcher[]>(response);
}

export async function listReviewers(search?: string): Promise<Researcher[]> {
  const url = new URL(`${API_BASE_URL}/api/v1/users/reviewers`);
  if (search) {
    url.searchParams.append("search", search);
  }
  const response = await fetch(url.toString(), {
    headers: getHeaders(),
  });
  return handleResponse<Researcher[]>(response);
}
