import type { TokenPair, UserMe, Institution, InstitutionUser, MessageResponse, ApiError, Publication, Project, Conference, DashboardSummary, Collaboration, Citation, Notification, ResearcherProfile, GlobalResearcher, Department, SearchResult } from "@/types";

// Configure API base URL - uses environment variable or defaults to localhost
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private getHeaders(): HeadersInit {
    const token = localStorage.getItem("access_token");
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = (await response.json().catch(() => ({}))) as ApiError | { detail?: string };
      const message =
        (errorData as ApiError).detail?.[0]?.msg ||
        (errorData as { detail?: string }).detail ||
        `HTTP ${response.status}: ${response.statusText}`;
      throw new Error(message);
    }
    if (response.status === 204) {
      return undefined as T;
    }
    return response.json() as Promise<T>;
  }

  // Auth
  async login(username: string, password: string): Promise<TokenPair> {
    const formData = new URLSearchParams();
    formData.append("grant_type", "password");
    formData.append("username", username);
    formData.append("password", password);

    const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData,
    });
    return this.handleResponse<TokenPair>(response);
  }

  async refreshToken(refresh_token: string): Promise<TokenPair> {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token }),
    });
    return this.handleResponse<TokenPair>(response);
  }

  async getMe(): Promise<UserMe> {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/me`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<UserMe>(response);
  }

  async listGlobalResearchers(): Promise<GlobalResearcher[]> { const response = await fetch(`${this.baseUrl}/api/v1/admin/researchers`, { headers: this.getHeaders() }); return this.handleResponse<GlobalResearcher[]>(response); }
  async listDepartments(): Promise<Department[]> { const response = await fetch(`${this.baseUrl}/api/v1/departments`, { headers: this.getHeaders() }); return this.handleResponse<Department[]>(response); }
  async createDepartment(data: { name: string; description?: string }): Promise<Department> { const response = await fetch(`${this.baseUrl}/api/v1/departments`, { method: "POST", headers: this.getHeaders(), body: JSON.stringify(data) }); return this.handleResponse<Department>(response); }
  async updateDepartment(id: string, data: { name: string; description?: string }): Promise<Department> { const response = await fetch(`${this.baseUrl}/api/v1/departments/${id}`, { method: "PATCH", headers: this.getHeaders(), body: JSON.stringify(data) }); return this.handleResponse<Department>(response); }
  async deleteDepartment(id: string): Promise<void> { const response = await fetch(`${this.baseUrl}/api/v1/departments/${id}`, { method: "DELETE", headers: this.getHeaders() }); return this.handleResponse<void>(response); }

  async verifyEmail(token: string): Promise<MessageResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/verify-email`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
    });
    return this.handleResponse<MessageResponse>(response);
  }

  async verifyInvite(token: string, password: string): Promise<MessageResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/verify-invite`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, password }),
    });
    return this.handleResponse<MessageResponse>(response);
  }

  async forgotPassword(email: string): Promise<MessageResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/forgot-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    return this.handleResponse<MessageResponse>(response);
  }

  async resetPassword(token: string, new_password: string): Promise<MessageResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/reset-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, new_password }),
    });
    return this.handleResponse<MessageResponse>(response);
  }

  // Institutions
  async registerInstitution(data: {
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

    const response = await fetch(`${this.baseUrl}/api/v1/institutions/register`, {
      method: "POST",
      body: formData,
    });
    return this.handleResponse<Institution>(response);
  }

  async listInstitutions(): Promise<Institution[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/institutions`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<Institution[]>(response);
  }

  async createInstitution(data: { name: string; address: string }): Promise<Institution> { const response = await fetch(`${this.baseUrl}/api/v1/institutions`, { method: "POST", headers: this.getHeaders(), body: JSON.stringify(data) }); return this.handleResponse<Institution>(response); }
  async getInstitution(institution_id: string): Promise<Institution> { const response = await fetch(`${this.baseUrl}/api/v1/institutions/${institution_id}`, { headers: this.getHeaders() }); return this.handleResponse<Institution>(response); }
  async updateInstitution(institution_id: string, data: { name: string; address: string; logo_url?: string | null }): Promise<Institution> { const response = await fetch(`${this.baseUrl}/api/v1/institutions/${institution_id}`, { method: "PATCH", headers: this.getHeaders(), body: JSON.stringify(data) }); return this.handleResponse<Institution>(response); }
  async deleteInstitution(institution_id: string): Promise<void> { const response = await fetch(`${this.baseUrl}/api/v1/institutions/${institution_id}`, { method: "DELETE", headers: this.getHeaders() }); return this.handleResponse<void>(response); }

  async activateInstitution(institution_id: string): Promise<Institution> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/institutions/${institution_id}/activate`,
      {
        method: "PATCH",
        headers: this.getHeaders(),
      }
    );
    return this.handleResponse<Institution>(response);
  }

  async deactivateInstitution(institution_id: string): Promise<Institution> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/institutions/${institution_id}/deactivate`,
      {
        method: "PATCH",
        headers: this.getHeaders(),
      }
    );
    return this.handleResponse<Institution>(response);
  }

  // Institution Users
  async createInstitutionUser(data: {
    email: string;
    full_name: string;
    role: "RESEARCHER" | "REVIEWER";
    description?: string;
  }): Promise<InstitutionUser> {
    const response = await fetch(`${this.baseUrl}/api/v1/institution/users`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    return this.handleResponse<InstitutionUser>(response);
  }

  async listInstitutionUsers(role?: "RESEARCHER" | "REVIEWER"): Promise<InstitutionUser[]> {
    const url = new URL(`${this.baseUrl}/api/v1/institution/users`);
    if (role) url.searchParams.append("role", role);

    const response = await fetch(url, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<InstitutionUser[]>(response);
  }

  async activateUser(user_id: string): Promise<InstitutionUser> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/institution/users/${user_id}/activate`,
      {
        method: "PATCH",
        headers: this.getHeaders(),
      }
    );
    return this.handleResponse<InstitutionUser>(response);
  }

  async deactivateUser(user_id: string): Promise<InstitutionUser> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/institution/users/${user_id}/deactivate`,
      {
        method: "PATCH",
        headers: this.getHeaders(),
      }
    );
    return this.handleResponse<InstitutionUser>(response);
  }

  async updateInstitutionUser(user_id: string, data: Partial<Pick<InstitutionUser, "full_name" | "description">>): Promise<InstitutionUser> { const response = await fetch(`${this.baseUrl}/api/v1/institution/users/${user_id}`, { method: "PATCH", headers: this.getHeaders(), body: JSON.stringify(data) }); return this.handleResponse<InstitutionUser>(response); }
  async deleteInstitutionUser(user_id: string): Promise<void> { const response = await fetch(`${this.baseUrl}/api/v1/institution/users/${user_id}`, { method: "DELETE", headers: this.getHeaders() }); return this.handleResponse<void>(response); }
  async getInstitutionResearcherProfile(user_id: string): Promise<ResearcherProfile> { const response = await fetch(`${this.baseUrl}/api/v1/institution/users/${user_id}/researcher-profile`, { headers: this.getHeaders() }); return this.handleResponse<ResearcherProfile>(response); }
  async updateInstitutionResearcherProfile(user_id: string, data: Pick<ResearcherProfile, "department" | "skills" | "research_interests" | "affiliations">): Promise<ResearcherProfile> { const response = await fetch(`${this.baseUrl}/api/v1/institution/users/${user_id}/researcher-profile`, { method: "PUT", headers: this.getHeaders(), body: JSON.stringify(data) }); return this.handleResponse<ResearcherProfile>(response); }

  private async research<T>(path: string, options: RequestInit = {}): Promise<T> { const response = await fetch(`${this.baseUrl}/api/v1/research${path}`, { ...options, headers: { ...this.getHeaders(), ...options.headers } }); return this.handleResponse<T>(response); }
  async getResearchDashboard(): Promise<DashboardSummary> { return this.research<DashboardSummary>("/dashboard"); }
  async getAnalytics(): Promise<any> { return this.research<any>("/analytics"); }
  async globalSearch(query: string): Promise<SearchResult[]> { return this.research<SearchResult[]>(`/search?query=${encodeURIComponent(query)}`); }
  async getResearcherProfile(): Promise<ResearcherProfile> { return this.research<ResearcherProfile>("/profile"); }
  async updateResearcherProfile(data: Pick<ResearcherProfile, "department" | "skills" | "research_interests" | "affiliations">): Promise<ResearcherProfile> { return this.research<ResearcherProfile>("/profile", { method: "PUT", body: JSON.stringify(data) }); }
  async listPublications(filters?: { query?: string; publication_type?: string; publication_status?: string }): Promise<Publication[]> { const params = new URLSearchParams(); if (filters?.query) params.set("query", filters.query); if (filters?.publication_type) params.set("publication_type", filters.publication_type); if (filters?.publication_status) params.set("publication_status", filters.publication_status); const suffix = params.size ? `?${params}` : ""; return this.research<Publication[]>(`/publications${suffix}`); }
  async createPublication(data: Partial<Publication>): Promise<Publication> { return this.research<Publication>("/publications", { method: "POST", body: JSON.stringify(data) }); }
  async updatePublication(id: string, data: Partial<Publication>): Promise<Publication> { return this.research<Publication>(`/publications/${id}`, { method: "PATCH", body: JSON.stringify(data) }); }
  async deletePublication(id: string): Promise<void> { return this.research<void>(`/publications/${id}`, { method: "DELETE" }); }
  async uploadPublicationFile(id: string, file: File): Promise<Publication> { const token = localStorage.getItem("access_token"); const form = new FormData(); form.append("file", file); const response = await fetch(`${this.baseUrl}/api/v1/research/publications/${id}/file`, { method: "POST", headers: token ? { Authorization: `Bearer ${token}` } : {}, body: form }); return this.handleResponse<Publication>(response); }
  async listProjects(): Promise<Project[]> { return this.research<Project[]>("/projects"); }
  async createProject(data: Partial<Project>): Promise<Project> { return this.research<Project>("/projects", { method: "POST", body: JSON.stringify(data) }); }
  async updateProject(id: string, data: Partial<Project>): Promise<Project> { return this.research<Project>(`/projects/${id}`, { method: "PATCH", body: JSON.stringify(data) }); }
  async deleteProject(id: string): Promise<void> { return this.research<void>(`/projects/${id}`, { method: "DELETE" }); }
  async listProjectAssignments(id: string): Promise<Array<{ id: string; user_id: string; role: string }>> { return this.research(`/projects/${id}/assignments`); }
  async assignProjectMember(id: string, data: { user_id: string; role: string }): Promise<unknown> { return this.research(`/projects/${id}/assignments`, { method: "POST", body: JSON.stringify(data) }); }
  async removeProjectMember(projectId: string, userId: string): Promise<void> { return this.research<void>(`/projects/${projectId}/assignments/${userId}`, { method: "DELETE" }); }
  async listConferences(): Promise<Conference[]> { return this.research<Conference[]>("/conferences"); }
  async createConference(data: Partial<Conference>): Promise<Conference> { return this.research<Conference>("/conferences", { method: "POST", body: JSON.stringify(data) }); }
  async updateConference(id: string, data: Partial<Conference>): Promise<Conference> { return this.research<Conference>(`/conferences/${id}`, { method: "PATCH", body: JSON.stringify(data) }); }
  async deleteConference(id: string): Promise<void> { return this.research<void>(`/conferences/${id}`, { method: "DELETE" }); }
  async listConferenceEvents(id: string): Promise<Array<{ id: string; title: string; starts_at: string; ends_at: string | null; description: string | null }>> { return this.research(`/conferences/${id}/events`); }
  async createConferenceEvent(id: string, data: { title: string; starts_at: string; ends_at?: string; description?: string }): Promise<unknown> { return this.research(`/conferences/${id}/events`, { method: "POST", body: JSON.stringify(data) }); }
  async deleteConferenceEvent(conferenceId: string, eventId: string): Promise<void> { return this.research<void>(`/conferences/${conferenceId}/events/${eventId}`, { method: "DELETE" }); }
  async listConferenceParticipations(id: string): Promise<Array<{ id: string; user_id: string; participation_type: string; presentation_title: string | null }>> { return this.research(`/conferences/${id}/participations`); }
  async registerConference(data: { conference_id: string; user_id: string; participation_type?: string; presentation_title?: string }): Promise<unknown> { return this.research("/conference-participations", { method: "POST", body: JSON.stringify(data) }); }
  async listCollaborations(): Promise<Collaboration[]> { return this.research<Collaboration[]>("/collaborations"); }
  async createCollaboration(data: Partial<Collaboration>): Promise<Collaboration> { return this.research<Collaboration>("/collaborations", { method: "POST", body: JSON.stringify(data) }); }
  async updateCollaboration(id: string, data: Partial<Collaboration>): Promise<Collaboration> { return this.research<Collaboration>(`/collaborations/${id}`, { method: "PATCH", body: JSON.stringify(data) }); }
  async deleteCollaboration(id: string): Promise<void> { return this.research<void>(`/collaborations/${id}`, { method: "DELETE" }); }
  async listCitations(): Promise<Citation[]> { return this.research<Citation[]>("/citations"); }
  async createCitation(data: Pick<Citation, "source_publication_id" | "cited_publication_id">): Promise<Citation> { return this.research<Citation>("/citations", { method: "POST", body: JSON.stringify(data) }); }
  async deleteCitation(id: string): Promise<void> { return this.research<void>(`/citations/${id}`, { method: "DELETE" }); }
  async listNotifications(): Promise<Notification[]> { return this.research<Notification[]>("/notifications"); }
  async markNotificationRead(id: string): Promise<Notification> { return this.research<Notification>(`/notifications/${id}/read`, { method: "PATCH" }); }
  async downloadReport(format: "pdf" | "xlsx"): Promise<Blob> { const response = await fetch(`${this.baseUrl}/api/v1/reports/publications.${format}`, { headers: this.getHeaders() }); if (!response.ok) throw new Error("Unable to generate report"); return response.blob(); }
  async getReport(kind: "summary" | "research" | "collaborations" | "institution"): Promise<Record<string, number>> { const response = await fetch(`${this.baseUrl}/api/v1/reports/${kind}`, { headers: this.getHeaders() }); return this.handleResponse<Record<string, number>>(response); }
}

export const apiClient = new ApiClient(API_BASE_URL);
