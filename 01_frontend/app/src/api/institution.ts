import { API_BASE_URL, getHeaders, handleResponse } from "./core";
import type { Institution } from "@/types";

export async function registerInstitution(data: {
  name: string;
  address: string;
  admin_full_name: string;
  admin_email: string;
  admin_password: string;
  logo: File;
}): Promise<Institution> {
  const formData = new FormData();
  formData.append("name", data.name);
  formData.append("address", data.address);
  formData.append("admin_full_name", data.admin_full_name);
  formData.append("admin_email", data.admin_email);
  formData.append("admin_password", data.admin_password);
  formData.append("logo", data.logo);

  const response = await fetch(`${API_BASE_URL}/api/v1/institutions/register`, {
    method: "POST",
    body: formData,
  });
  return handleResponse<Institution>(response);
}

export async function listInstitutions(): Promise<Institution[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/institutions`, {
    headers: getHeaders(),
  });
  return handleResponse<Institution[]>(response);
}

export async function activateInstitution(institution_id: string): Promise<Institution> {
  const response = await fetch(`${API_BASE_URL}/api/v1/institutions/${institution_id}/activate`, {
    method: "PATCH",
    headers: getHeaders(),
  });
  return handleResponse<Institution>(response);
}

export async function deactivateInstitution(institution_id: string): Promise<Institution> {
  const response = await fetch(`${API_BASE_URL}/api/v1/institutions/${institution_id}/deactivate`, {
    method: "PATCH",
    headers: getHeaders(),
  });
  return handleResponse<Institution>(response);
}
