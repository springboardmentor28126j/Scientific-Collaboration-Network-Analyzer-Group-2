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

// Publications

export type PublicationType =
  | "JOURNAL"
  | "CONFERENCE"
  | "BOOK"
  | "PATENT"
  | "TECHNICAL_REPORT";

export type PublicationStatus =
  | "DRAFT"
  | "SUBMITTED"
  | "UNDER_REVIEW"
  | "REVISION_REQUIRED"
  | "ACCEPTED"
  | "REJECTED"
  | "PUBLISHED"
  | "ARCHIVED";

export interface PublicationListItem {
  id: string;
  title: string;
  publication_type: PublicationType;
  status: PublicationStatus;
  created_at: string;
}

export interface PublicationRead {
  id: string;
  title: string;
  abstract: string;
  publication_type: PublicationType;
  status: PublicationStatus;
  doi: string | null;
  pdf_url: string | null;
  created_by: string;
  submitted_at: string | null;
  published_at: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface PublicationUpdate {
  title?: string | null;
  abstract?: string | null;
  publication_type?: PublicationType | null;
  doi?: string | null;
  pdf_url?: string | null;
}

export interface PublicationAuthorCreate {
  researcher_id: string;
  author_order: number;
  is_corresponding_author?: boolean;
}

export interface PublicationAuthorRead {
  researcher_id: string;
  full_name: string;
  institution: string | null;
  author_order: number;
  is_corresponding_author: boolean;
}

export interface HistoryUserRead {
  id: string;
  full_name: string;
}

export type PublicationHistoryAction =
  | "CREATED"
  | "UPDATED"
  | "PDF_UPDATED"
  | "AUTHOR_ADDED"
  | "AUTHOR_REMOVED"
  | "SUBMITTED"
  | "RESUBMITTED"
  | "REVIEWER_ASSIGNED"
  | "REVIEWER_UNASSIGNED"
  | "REVIEW_SUBMITTED"
  | "REVISION_REQUESTED"
  | "ACCEPTED"
  | "REJECTED"
  | "PUBLISHED"
  | "ARCHIVED"
  | "CONFERENCE_CREATED"
  | "CONFERENCE_UPDATED";

export interface PublicationHistoryRead {
  id: string;
  publication_id: string;
  action: PublicationHistoryAction;
  description: string;
  created_at: string;
  user: HistoryUserRead | null;
}

export interface Researcher {
  id: string;
  full_name: string;
  email: string;
  description: string | null;
  institution_name: string | null;
}
