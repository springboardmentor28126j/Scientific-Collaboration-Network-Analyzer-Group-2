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
