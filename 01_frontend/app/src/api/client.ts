import type { 
  TokenPair, 
  UserMe, 
  Institution, 
  InstitutionUser, 
  MessageResponse, 
  ApiError,
  PublicationListItem,
  PublicationRead,
  PublicationUpdate,
  PublicationAuthorCreate,
  PublicationAuthorRead,
  PublicationHistoryRead,
  Researcher
} from "@/types";

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

  // Publications
  async listPublications(): Promise<PublicationListItem[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/publications`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<PublicationListItem[]>(response);
  }

  async createPublication(data: FormData): Promise<PublicationRead> {
    // Note: FormData does not need Content-Type set manually; the browser will set it with the correct boundary
    const token = localStorage.getItem("access_token");
    const headers: HeadersInit = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseUrl}/api/v1/publications`, {
      method: "POST",
      headers,
      body: data,
    });
    return this.handleResponse<PublicationRead>(response);
  }

  async getPublication(id: string): Promise<PublicationRead> {
    const response = await fetch(`${this.baseUrl}/api/v1/publications/${id}`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<PublicationRead>(response);
  }

  async updatePublication(id: string, data: PublicationUpdate): Promise<PublicationRead> {
    const response = await fetch(`${this.baseUrl}/api/v1/publications/${id}`, {
      method: "PUT",
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    return this.handleResponse<PublicationRead>(response);
  }

  async deletePublication(id: string): Promise<MessageResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/publications/${id}`, {
      method: "DELETE",
      headers: this.getHeaders(),
    });
    return this.handleResponse<MessageResponse>(response);
  }

  // Publication Authors
  async addPublicationAuthor(id: string, data: PublicationAuthorCreate): Promise<PublicationAuthorRead> {
    const response = await fetch(`${this.baseUrl}/api/v1/publications/${id}/authors`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    return this.handleResponse<PublicationAuthorRead>(response);
  }

  async listPublicationAuthors(id: string): Promise<PublicationAuthorRead[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/publications/${id}/authors`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<PublicationAuthorRead[]>(response);
  }

  async removePublicationAuthor(id: string, researcher_id: string): Promise<MessageResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/publications/${id}/authors/${researcher_id}`, {
      method: "DELETE",
      headers: this.getHeaders(),
    });
    return this.handleResponse<MessageResponse>(response);
  }

  // Publication Actions
  async submitPublication(id: string): Promise<PublicationRead> {
    const response = await fetch(`${this.baseUrl}/api/v1/publications/${id}/submit`, {
      method: "POST",
      headers: this.getHeaders(),
    });
    return this.handleResponse<PublicationRead>(response);
  }

  async getPublicationHistory(id: string): Promise<PublicationHistoryRead[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/publications/${id}/history`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<PublicationHistoryRead[]>(response);
  }

  // Users / Researchers
  async listResearchers(search?: string): Promise<Researcher[]> {
    const url = new URL(`${this.baseUrl}/api/v1/users/researchers`);
    if (search) {
      url.searchParams.append("search", search);
    }
    const response = await fetch(url, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<Researcher[]>(response);
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
