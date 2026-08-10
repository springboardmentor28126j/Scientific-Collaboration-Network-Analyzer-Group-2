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

export interface CatalogPublication {
  id: string;
  title: string;
  publication_type: string;
  doi: string | null;
  published_at: string;
}

export interface CatalogPublicationDetail {
  id: string;
  title: string;
  abstract?: string;
  authors: string;
  institution_name?: string;
  publication_name: string | null;
  year: number;
  doi: string | null;
  url: string;
  publication_type: string;
}

export interface ListCatalogParams {
  page?: number;
  size?: number;
  search?: string;
  publication_type?: string;
  sort_by?: string;
  order?: "asc" | "desc";
}

export interface CatalogSearchItem {
  id: string;
  title: string;
  doi: string | null;
  publication_type: string;
  published_at: string;
}

export interface ReferenceRead {
  id: string;
  reference_order: number;
  title: string;
  authors: string;
  publication_name: string | null;
  year: number;
  doi: string | null;
  url: string | null;
}

export interface ReferenceCreate {
  title: string;
  authors: string;
  publication_name?: string | null;
  year: number;
  doi?: string | null;
  url?: string | null;
}

export interface ReferenceUpdate extends ReferenceCreate {
  reference_order?: number;
}

export async function listPublications(params?: ListPublicationsParams): Promise<PaginatedResponse<PublicationRead>> {
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        searchParams.append(key, String(value));
      }
    });
  }

  const queryString = searchParams.toString();
  const url = queryString 
    ? `${API_BASE_URL}/api/v1/publications?${queryString}`
    : `${API_BASE_URL}/api/v1/publications`;

  const response = await fetch(url, {
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

export async function getCatalogPublications(params: ListCatalogParams): Promise<PaginatedResponse<CatalogPublication>> {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.append(key, String(value));
    }
  });

  const queryString = searchParams.toString();
  const url = queryString 
    ? `${API_BASE_URL}/api/v1/publications/catalog?${queryString}`
    : `${API_BASE_URL}/api/v1/publications/catalog`;

  const response = await fetch(url, {
    headers: getHeaders(),
  });
  return handleResponse<PaginatedResponse<CatalogPublication>>(response);
}

export async function getCatalogPublication(id: string): Promise<CatalogPublicationDetail> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications/catalog/${id}`, {
    headers: getHeaders(),
  });
  return handleResponse<CatalogPublicationDetail>(response);
}

export async function searchCatalog(query: string): Promise<CatalogSearchItem[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications/catalog/search?search=${encodeURIComponent(query)}`, {
    headers: getHeaders(),
  });
  return handleResponse<CatalogSearchItem[]>(response);
}

export async function listReferences(publicationId: string): Promise<ReferenceRead[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications/${publicationId}/references`, {
    headers: getHeaders(),
  });
  return handleResponse<ReferenceRead[]>(response);
}

export async function addReference(publicationId: string, data: ReferenceCreate): Promise<ReferenceRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications/${publicationId}/references`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ReferenceRead>(response);
}

export async function updateReference(publicationId: string, referenceId: string, data: ReferenceUpdate): Promise<ReferenceRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications/${publicationId}/references/${referenceId}`, {
    method: "PUT",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ReferenceRead>(response);
}

export async function deleteReference(publicationId: string, referenceId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/publications/${publicationId}/references/${referenceId}`, {
    method: "DELETE",
    headers: getHeaders(),
  });
  return handleResponse<void>(response);
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
