// User roles
export type UserRole = "SUPER_ADMIN" | "INSTITUTION_ADMIN" | "RESEARCHER" | "REVIEWER";

// Token response from login/refresh
export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Authenticated user from /auth/me
export interface UserMe {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  description: string | null;
  institution_id: string | null;
  is_verified: boolean;
  is_active: boolean;
  created_at: string;
}

// Institution
export interface Institution {
  id: string;
  name: string;
  address: string;
  logo_url: string | null;
  is_active: boolean;
  created_at: string;
}

// Institution User (Researcher/Reviewer)
export interface InstitutionUser {
  id: string;
  email: string;
  full_name: string;
  role: string;
  description: string | null;
  is_verified: boolean;
  is_active: boolean;
  created_at: string;
}

// API Error
export interface ApiError {
  detail: Array<{
    loc: (string | number)[];
    msg: string;
    type: string;
    input: unknown;
    ctx: Record<string, unknown>;
  }>;
}

export interface MessageResponse {
  detail: string;
}
