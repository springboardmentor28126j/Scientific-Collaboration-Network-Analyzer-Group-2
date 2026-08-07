import { API_BASE_URL, getHeaders, handleResponse } from "./core";

export interface PublicationStatusStats {
  draft: number;
  submitted: number;
  under_review: number;
  revision_required: number;
  accepted: number;
  rejected: number;
  published: number;
  archived: number;
}

export interface TopResearcher {
  id: string;
  full_name: string;
  institution_name: string;
  published_papers: number;
}

export interface SuperAdminDashboard {
  total_publications: number;
  publication_status: PublicationStatusStats;
  total_institutions: number;
  total_researchers: number;
  total_reviewers: number;
  top_researchers?: TopResearcher[];
}

export interface InstitutionDashboard {
  total_publications: number;
  publication_status: PublicationStatusStats;
  total_researchers: number;
  total_reviewers: number;
  top_researchers?: TopResearcher[];
}

export interface ResearcherDashboard {
  my_publications: number;
  publication_status: PublicationStatusStats;
  coauthored_publications: number;
}

export interface ReviewerDashboard {
  assigned_reviews: number;
  pending_reviews: number;
  completed_reviews: number;
}

export async function getDashboard(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/v1/dashboard`, {
    headers: getHeaders(),
  });
  return handleResponse<any>(response);
}
