import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/api/client";
import { toast } from "sonner";
import type {
  PublicationListItem,
  PublicationRead,
  PublicationUpdate,
  PublicationAuthorCreate,
  PublicationAuthorRead,
  PublicationHistoryRead,
  Researcher,
} from "@/types";

// --- Publications ---

export function usePublications() {
  return useQuery<PublicationListItem[]>({
    queryKey: ["publications"],
    queryFn: () => apiClient.listPublications(),
  });
}

export function usePublication(id: string) {
  return useQuery<PublicationRead>({
    queryKey: ["publications", id],
    queryFn: () => apiClient.getPublication(id),
    enabled: !!id,
  });
}

export function useCreatePublication() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: FormData) => apiClient.createPublication(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["publications"] });
      toast.success("Publication created successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to create publication");
    },
  });
}

export function useUpdatePublication() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: PublicationUpdate }) =>
      apiClient.updatePublication(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["publications"] });
      queryClient.invalidateQueries({ queryKey: ["publications", variables.id] });
      toast.success("Publication updated successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to update publication");
    },
  });
}

export function useDeletePublication() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiClient.deletePublication(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["publications"] });
      toast.success("Publication deleted successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to delete publication");
    },
  });
}

export function useSubmitPublication() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiClient.submitPublication(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["publications"] });
      queryClient.invalidateQueries({ queryKey: ["publications", id] });
      queryClient.invalidateQueries({ queryKey: ["publication-history", id] });
      toast.success("Publication submitted for review");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to submit publication");
    },
  });
}

// --- Publication Authors ---

export function usePublicationAuthors(id: string) {
  return useQuery<PublicationAuthorRead[]>({
    queryKey: ["publication-authors", id],
    queryFn: () => apiClient.listPublicationAuthors(id),
    enabled: !!id,
  });
}

export function useAddPublicationAuthor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: PublicationAuthorCreate }) =>
      apiClient.addPublicationAuthor(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["publication-authors", variables.id] });
      queryClient.invalidateQueries({ queryKey: ["publication-history", variables.id] });
      toast.success("Author added successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to add author");
    },
  });
}

export function useRemovePublicationAuthor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, researcher_id }: { id: string; researcher_id: string }) =>
      apiClient.removePublicationAuthor(id, researcher_id),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["publication-authors", variables.id] });
      queryClient.invalidateQueries({ queryKey: ["publication-history", variables.id] });
      toast.success("Author removed successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to remove author");
    },
  });
}

// --- Publication History ---

export function usePublicationHistory(id: string) {
  return useQuery<PublicationHistoryRead[]>({
    queryKey: ["publication-history", id],
    queryFn: () => apiClient.getPublicationHistory(id),
    enabled: !!id,
  });
}

// --- Researchers ---

export function useResearchers(search?: string) {
  return useQuery<Researcher[]>({
    queryKey: ["researchers", search],
    queryFn: () => apiClient.listResearchers(search),
  });
}
