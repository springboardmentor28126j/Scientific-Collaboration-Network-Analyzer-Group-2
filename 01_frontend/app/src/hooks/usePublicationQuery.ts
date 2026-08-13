import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  listPublications,
  createPublication,
  getPublication,
  updatePublication,
  deletePublication,
  submitPublication,
  addPublicationAuthor,
  listPublicationAuthors,
  removePublicationAuthor,
  getPublicationHistory,
  publishPublication,
  createConference,
  updateConference,
  getConference,
  submitEditorialDecision,
  archivePublication,
  downloadPublicationPdf,
  getCatalogPublications,
  getCatalogPublication,
  listReferences,
  addReference,
  updateReference,
  deleteReference,
  searchCatalog,
} from "@/api/publication";
import type { ListPublicationsParams, ListCatalogParams, ReferenceCreate, ReferenceUpdate } from "@/api/publication";
import { listResearchers } from "@/api/user";
import { toast } from "sonner";
import type {
  PublicationRead,
  PublicationUpdate,
  PublicationAuthorCreate,
  PublicationAuthorRead,
  PublicationHistoryRead,
  PaginatedResponse,
  Researcher,
  ConferenceCreate,
  ConferenceRead,
  EditorialDecisionCreate,
} from "@/types";

// --- Publications ---

export function usePublications(params?: ListPublicationsParams) {
  return useQuery<PaginatedResponse<PublicationRead>>({
    queryKey: ["publications", params],
    queryFn: () => listPublications(params),
  });
}

export function usePublication(id: string) {
  return useQuery<PublicationRead>({
    queryKey: ["publications", id],
    queryFn: () => getPublication(id),
    enabled: !!id,
  });
}

export function useCreatePublication() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: FormData) => createPublication(data),
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
      updatePublication(id, data),
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
    mutationFn: (id: string) => deletePublication(id),
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
    mutationFn: (id: string) => submitPublication(id),
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
    queryFn: () => listPublicationAuthors(id),
    enabled: !!id,
  });
}

export function useAddPublicationAuthor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: PublicationAuthorCreate }) =>
      addPublicationAuthor(id, data),
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
      removePublicationAuthor(id, researcher_id),
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
    queryFn: () => getPublicationHistory(id),
    enabled: !!id,
  });
}

export function usePublishPublication() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => publishPublication(id),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["publications"] });
      queryClient.invalidateQueries({ queryKey: ["publications", data.id] });
      queryClient.invalidateQueries({ queryKey: ["publication-history", data.id] });
      toast.success("Publication published successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to publish publication");
    },
  });
}

export function useArchivePublication() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => archivePublication(id),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["publications"] });
      queryClient.invalidateQueries({ queryKey: ["publications", data.id] });
      queryClient.invalidateQueries({ queryKey: ["publication-history", data.id] });
      toast.success("Publication archived successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to archive publication");
    },
  });
}

export function useDownloadPdf() {
  return useMutation({
    mutationFn: (id: string) => downloadPublicationPdf(id),
    onError: (error: Error) => {
      toast.error(error.message || "Failed to download PDF");
    },
  });
}

export function useConference(publicationId: string) {
  return useQuery<ConferenceRead>({
    queryKey: ["conference", publicationId],
    queryFn: () => getConference(publicationId),
    enabled: !!publicationId,
    retry: false, // Prevent retrying if conference is 404 (doesn't exist yet)
  });
}

export function useCreateConference() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ConferenceCreate }) => createConference(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["conference", variables.id] });
      toast.success("Conference details added successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to add conference details");
    },
  });
}

export function useCatalogPublications(params: ListCatalogParams) {
  return useQuery({
    queryKey: ["catalog", params],
    queryFn: () => getCatalogPublications(params),
    placeholderData: (previousData) => previousData,
  });
}

export function useCatalogPublication(id: string) {
  return useQuery({
    queryKey: ["catalog", id],
    queryFn: () => getCatalogPublication(id),
    enabled: !!id,
  });
}

export function useUpdateConference() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ConferenceCreate }) => updateConference(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["conference", variables.id] });
      toast.success("Conference details updated successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to update conference details");
    },
  });
}

export function useReferences(publicationId: string) {
  return useQuery({
    queryKey: ["references", publicationId],
    queryFn: () => listReferences(publicationId),
    enabled: !!publicationId,
  });
}

export function useAddReference(publicationId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ReferenceCreate) => addReference(publicationId, data),
    onSuccess: () => {
      toast.success("Reference added successfully");
      queryClient.invalidateQueries({ queryKey: ["references", publicationId] });
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });
}

export function useUpdateReference(publicationId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ referenceId, data }: { referenceId: string; data: ReferenceUpdate }) =>
      updateReference(publicationId, referenceId, data),
    onSuccess: () => {
      toast.success("Reference updated successfully");
      queryClient.invalidateQueries({ queryKey: ["references", publicationId] });
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });
}

export function useDeleteReference(publicationId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (referenceId: string) => deleteReference(publicationId, referenceId),
    onSuccess: () => {
      toast.success("Reference removed successfully");
      queryClient.invalidateQueries({ queryKey: ["references", publicationId] });
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });
}

export function useSearchCatalog(query: string) {
  return useQuery({
    queryKey: ["catalog-search", query],
    queryFn: () => searchCatalog(query),
    enabled: query.length >= 3,
    staleTime: 30000,
  });
}

export function useSubmitEditorialDecision() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: EditorialDecisionCreate }) => submitEditorialDecision(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["publications"] });
      queryClient.invalidateQueries({ queryKey: ["publications", data.id] });
      queryClient.invalidateQueries({ queryKey: ["publication-history", data.id] });
      toast.success("Editorial decision submitted successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to submit editorial decision");
    },
  });
}

// --- Researchers ---

export function useResearchers(search?: string) {
  return useQuery<Researcher[]>({
    queryKey: ["researchers", search],
    queryFn: () => listResearchers(search),
  });
}
