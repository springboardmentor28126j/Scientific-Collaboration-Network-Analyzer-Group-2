import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  assignReviewers,
  listReviewAssignments,
  getMyReviewAssignments,
  submitReview,
  getReview,
  getPublicationReviews,
} from "@/api/review";
import { listReviewers } from "@/api/user";
import { toast } from "sonner";
import type { ReviewAssignmentRead, Researcher, ReviewCreate, ReviewRead } from "@/types";

export function useReviewers(search?: string) {
  return useQuery<Researcher[]>({
    queryKey: ["reviewers", search],
    queryFn: () => listReviewers(search),
  });
}

export function useReviewAssignments(publicationId: string) {
  return useQuery<ReviewAssignmentRead[]>({
    queryKey: ["review-assignments", publicationId],
    queryFn: () => listReviewAssignments(publicationId),
    enabled: !!publicationId,
  });
}

export function useAssignReviewers() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ publicationId, reviewerIds }: { publicationId: string; reviewerIds: string[] }) =>
      assignReviewers(publicationId, reviewerIds),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["review-assignments", variables.publicationId] });
      queryClient.invalidateQueries({ queryKey: ["publications"] });
      queryClient.invalidateQueries({ queryKey: ["publications", variables.publicationId] });
      queryClient.invalidateQueries({ queryKey: ["publication-history", variables.publicationId] });
      toast.success("Reviewers assigned successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to assign reviewers");
    },
  });
}

export function useMyReviewAssignments() {
  return useQuery<ReviewAssignmentRead[]>({
    queryKey: ["review-assignments", "my"],
    queryFn: () => getMyReviewAssignments(),
  });
}

export function useSubmitReview() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ReviewCreate) => submitReview(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["review-assignments"] });
      queryClient.invalidateQueries({ queryKey: ["publication-reviews"] });
      toast.success("Review submitted successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to submit review");
    },
  });
}

export function useReview(reviewId: string) {
  return useQuery<ReviewRead>({
    queryKey: ["reviews", reviewId],
    queryFn: () => getReview(reviewId),
    enabled: !!reviewId,
  });
}

export function usePublicationReviews(publicationId: string) {
  return useQuery<ReviewRead[]>({
    queryKey: ["publication-reviews", publicationId],
    queryFn: () => getPublicationReviews(publicationId),
    enabled: !!publicationId,
  });
}
