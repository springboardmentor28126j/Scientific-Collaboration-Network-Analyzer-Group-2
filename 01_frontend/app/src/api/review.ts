import { API_BASE_URL, getHeaders, handleResponse } from "./core";
import type { ReviewAssignmentRead, ReviewCreate, ReviewRead } from "@/types";

export async function assignReviewers(
  publicationId: string,
  reviewerIds: string[]
): Promise<ReviewAssignmentRead[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/review-assignments/publications/${publicationId}`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ reviewer_ids: reviewerIds }),
  });
  return handleResponse<ReviewAssignmentRead[]>(response);
}

export async function listReviewAssignments(
  publicationId: string
): Promise<ReviewAssignmentRead[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/review-assignments/publication/${publicationId}`, {
    headers: getHeaders(),
  });
  return handleResponse<ReviewAssignmentRead[]>(response);
}

export async function getMyReviewAssignments(): Promise<ReviewAssignmentRead[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/review-assignments/my`, {
    headers: getHeaders(),
  });
  return handleResponse<ReviewAssignmentRead[]>(response);
}

export async function submitReview(data: ReviewCreate): Promise<ReviewRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/reviews`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ReviewRead>(response);
}

export async function getReview(review_id: string): Promise<ReviewRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/reviews/${review_id}`, {
    headers: getHeaders(),
  });
  return handleResponse<ReviewRead>(response);
}

export async function getPublicationReviews(publication_id: string): Promise<ReviewRead[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/reviews/publication/${publication_id}`, {
    headers: getHeaders(),
  });
  return handleResponse<ReviewRead[]>(response);
}
