import { API_BASE_URL, getHeaders, handleResponse } from "./core";
import type {
  PublicationRead,
  PublicationUpdate,
  PublicationAuthorCreate,
  PublicationAuthorRead,
  PublicationHistoryRead,
  PaginatedResponse,
  MessageResponse,
  ConferenceCreate,
  ConferenceRead,
  EditorialDecisionCreate,
} from "@/types";

export interface ListPublicationsParams {
  page?: number;
  size?: number;
  search?: string;
  status?: string;
  publication_type?: string;
  institution_id?: string;
  sort_by?: string;
  order?: "asc" | "desc";
}

export async function listPublications(params?: ListPublicationsParams): Promise<PaginatedResponse<PublicationRead>> {
  const url = new URL(`${API_BASE_URL}/api/v1/publications`);
  
  if (params) {
    if (params.page) url.searchParams.append("page", params.page.toString());
    if (params.size) url.searchParams.append("size", params.size.toString());
    if (params.search) url.searchParams.append("search", params.search);
    if (params.status) url.searchParams.append("status", params.status);
    if (params.publication_type) url.searchParams.append("publication_type", params.publication_type);
    if (params.institution_id) url.searchParams.append("institution_id", params.institution_id);
    if (params.sort_by) url.searchParams.append("sort_by", params.sort_by);
    if (params.order) url.searchParams.append("order", params.order);
  }

  const response = await fetch(url.toString(), {
    headers: getHeaders(),
  });
  return handleResponse<PaginatedResponse<PublicationRead>>(response);
}

export async function createPublication(data: FormData): Promise<PublicationRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications`, {
    method: "POST",
    headers: getHeaders(true),
    body: data,
  });
  return handleResponse<PublicationRead>(response);
}

export async function getPublication(id: string): Promise<PublicationRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications/${id}`, {
    headers: getHeaders(),
  });
  return handleResponse<PublicationRead>(response);
}

export async function updatePublication(id: string, data: PublicationUpdate): Promise<PublicationRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications/${id}`, {
    method: "PUT",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<PublicationRead>(response);
}

export async function deletePublication(id: string): Promise<MessageResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications/${id}`, {
    method: "DELETE",
    headers: getHeaders(),
  });
  return handleResponse<MessageResponse>(response);
}

export async function addPublicationAuthor(id: string, data: PublicationAuthorCreate): Promise<PublicationAuthorRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications/${id}/authors`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<PublicationAuthorRead>(response);
}

export async function listPublicationAuthors(id: string): Promise<PublicationAuthorRead[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications/${id}/authors`, {
    headers: getHeaders(),
  });
  return handleResponse<PublicationAuthorRead[]>(response);
}

export async function removePublicationAuthor(id: string, researcher_id: string): Promise<MessageResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications/${id}/authors/${researcher_id}`, {
    method: "DELETE",
    headers: getHeaders(),
  });
  return handleResponse<MessageResponse>(response);
}

export async function submitPublication(id: string): Promise<PublicationRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications/${id}/submit`, {
    method: "POST",
    headers: getHeaders(),
  });
  return handleResponse<PublicationRead>(response);
}

export async function getPublicationHistory(id: string): Promise<PublicationHistoryRead[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications/${id}/history`, {
    headers: getHeaders(),
  });
  return handleResponse<PublicationHistoryRead[]>(response);
}

export async function publishPublication(id: string): Promise<PublicationRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications/${id}/publish`, {
    method: "PATCH",
    headers: getHeaders(),
  });
  return handleResponse<PublicationRead>(response);
}

export async function archivePublication(id: string): Promise<PublicationRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications/${id}/archive`, {
    method: "PATCH",
    headers: getHeaders(),
  });
  return handleResponse<PublicationRead>(response);
}

export async function downloadPublicationPdf(id: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications/${id}/download`, {
    headers: getHeaders(),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to download PDF");
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  window.open(url, "_blank");
  
  // Cleanup the object URL after a short delay
  setTimeout(() => {
    URL.revokeObjectURL(url);
  }, 1000);
}

// Due to the provided swagger docs we use the /publications/publications/ prefix for conference
export async function createConference(publication_id: string, data: ConferenceCreate): Promise<ConferenceRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications/publications/${publication_id}/conference`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ConferenceRead>(response);
}

export async function updateConference(publication_id: string, data: ConferenceCreate): Promise<ConferenceRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications/publications/${publication_id}/conference`, {
    method: "PATCH",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ConferenceRead>(response);
}

export async function getConference(publication_id: string): Promise<ConferenceRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications/publications/${publication_id}/conference`, {
    headers: getHeaders(),
  });
  return handleResponse<ConferenceRead>(response);
}

export async function submitEditorialDecision(publication_id: string, data: EditorialDecisionCreate): Promise<PublicationRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications/${publication_id}/decision`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<PublicationRead>(response);
}
