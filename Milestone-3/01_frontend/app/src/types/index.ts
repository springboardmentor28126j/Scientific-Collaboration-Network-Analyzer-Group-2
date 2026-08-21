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

export interface Publication { id: string; title: string; abstract: string | null; status: string; publication_type: string; doi: string | null; published_on: string | null; file_url: string | null; author_ids: string[]; created_at: string; }
export interface Project { id: string; name: string; description: string | null; funding_source: string | null; status: string; start_date: string | null; end_date: string | null; member_ids: string[]; created_at: string; }
export interface Conference { id: string; name: string; location: string | null; starts_on: string; ends_on: string | null; website_url: string | null; created_at: string; }
export interface Collaboration { id: string; partner_name: string; description: string | null; status: string; created_at: string; }
export interface Citation { id: string; source_publication_id: string; cited_publication_id: string; created_at: string; }
export interface Notification { id: string; title: string; message: string; is_read: boolean; link: string | null; created_at: string; }
export interface SearchResult { id: string; type: "Institution" | "Researcher" | "Publication" | "Conference" | "Project"; title: string; subtitle: string; path: string; }
export interface ResearcherProfile { id: string; user_id: string; department: string | null; skills: string[]; research_interests: string[]; affiliations: string[]; }
export interface GlobalResearcher extends InstitutionUser { institution_name: string | null; }
export interface Department { id: string; institution_id: string; name: string; description: string | null; created_at: string; }
export interface DashboardSummary { researchers: number; publications: number; active_projects: number; conferences: number; collaborations: number; citations: number; }
