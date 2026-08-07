import { z } from "zod";

// Login schema
export const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(1, "Password is required"),
});

export type LoginFormData = z.infer<typeof loginSchema>;

// Forgot password schema
export const forgotPasswordSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
});

export type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;

// Reset password schema
export const resetPasswordSchema = z
  .object({
    token: z.string().min(1, "Token is required"),
    new_password: z.string().min(8, "Password must be at least 8 characters").max(128),
    confirm_password: z.string(),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

export type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;

// Verify invite schema
export const verifyInviteSchema = z
  .object({
    token: z.string().min(1, "Token is required"),
    password: z.string().min(8, "Password must be at least 8 characters").max(128),
    confirm_password: z.string(),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

export type VerifyInviteFormData = z.infer<typeof verifyInviteSchema>;

// Institution registration schema
export const institutionRegisterSchema = z.object({
  name: z.string().min(1, "Institution name is required").max(255),
  address: z.string().min(1, "Address is required"),
  admin_full_name: z.string().min(1, "Admin full name is required"),
  admin_email: z.string().email("Please enter a valid email address"),
  admin_password: z.string().min(8, "Password must be at least 8 characters"),
});

export type InstitutionRegisterFormData = z.infer<typeof institutionRegisterSchema>;

// Create institution user (Researcher/Reviewer) schema
export const createUserSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  full_name: z.string().min(1, "Full name is required").max(255),
  role: z.enum(["RESEARCHER", "REVIEWER"] as const, {
    error: "Please select a role",
  }),
  description: z.string().optional(),
});

export type CreateUserFormData = z.infer<typeof createUserSchema>;

// Verify email query param schema
export const verifyEmailSchema = z.object({
  token: z.string().min(1, "Token is required"),
});

export type VerifyEmailFormData = z.infer<typeof verifyEmailSchema>;

// Publication schemas
export const publicationTypes = [
  "JOURNAL",
  "CONFERENCE",
  "BOOK",
  "PATENT",
  "TECHNICAL_REPORT",
] as const;

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ACCEPTED_PDF_TYPES = ["application/pdf"];

export const createPublicationSchema = z.object({
  title: z.string().min(1, "Title is required").max(500),
  abstract: z.string().min(1, "Abstract is required"),
  publication_type: z.enum(publicationTypes, {
    error: "Please select a valid publication type",
  }),
  doi: z.string().optional(),
  pdf: z
    .custom<FileList>((val) => val instanceof FileList, "Please upload a file")
    .refine((files) => files.length > 0, "PDF file is required")
    .refine((files) => files[0]?.size <= MAX_FILE_SIZE, "Max file size is 10MB")
    .refine(
      (files) => ACCEPTED_PDF_TYPES.includes(files[0]?.type),
      "Only .pdf files are accepted"
    ),
});

export type CreatePublicationFormData = z.infer<typeof createPublicationSchema>;

export const updatePublicationSchema = z.object({
  title: z.string().min(1, "Title is required").max(500).optional(),
  abstract: z.string().min(1, "Abstract is required").optional(),
  publication_type: z.enum(publicationTypes).optional(),
  doi: z.string().optional(),
});

export type UpdatePublicationFormData = z.infer<typeof updatePublicationSchema>;

export const addAuthorSchema = z.object({
  researcher_id: z.string().uuid("Invalid researcher ID"),
  author_order: z.number().int().min(1, "Author order must be at least 1"),
  is_corresponding_author: z.boolean().default(false),
});

export type AddAuthorFormData = z.infer<typeof addAuthorSchema>;

export const referenceSchema = z.object({
  title: z.string().min(1, "Title is required").max(500),
  authors: z.string().min(1, "Authors are required"),
  publication_name: z.string().nullable().optional(),
  year: z.number().int().min(1800, "Year must be valid").max(new Date().getFullYear() + 1),
  doi: z.string().nullable().optional(),
  url: z.string().url("Must be a valid URL").nullable().optional(),
});

export type ReferenceFormData = z.infer<typeof referenceSchema>;
