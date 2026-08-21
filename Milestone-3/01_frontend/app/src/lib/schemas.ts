import { z } from "zod";

const passwordSchema = z.string().min(8, "Password must be at least 8 characters");

export const loginSchema = z.object({
  email: z.email("Enter a valid email address"),
  password: z.string().min(1, "Password is required"),
});

export const forgotPasswordSchema = z.object({
  email: z.email("Enter a valid email address"),
});

export const institutionRegisterSchema = z.object({
  name: z.string().min(2, "Institution name is required"),
  address: z.string().min(5, "Address is required"),
  admin_full_name: z.string().min(2, "Full name is required"),
  admin_email: z.email("Enter a valid admin email"),
  admin_password: passwordSchema,
});

export const createUserSchema = z.object({
  email: z.email("Enter a valid email address"),
  full_name: z.string().min(2, "Full name is required"),
  role: z.enum(["RESEARCHER", "REVIEWER"]),
  description: z.string().max(500, "Description must be 500 characters or fewer").optional(),
});

export const verifyInviteSchema = z
  .object({
    token: z.string().min(1, "Invite token is missing"),
    password: passwordSchema,
    confirm_password: z.string(),
  })
  .refine((values) => values.password === values.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

export const resetPasswordSchema = z
  .object({
    token: z.string().min(1, "Reset token is missing"),
    new_password: passwordSchema,
    confirm_password: z.string(),
  })
  .refine((values) => values.new_password === values.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

export type LoginFormData = z.infer<typeof loginSchema>;
export type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;
export type InstitutionRegisterFormData = z.infer<typeof institutionRegisterSchema>;
export type CreateUserFormData = z.infer<typeof createUserSchema>;
export type VerifyInviteFormData = z.infer<typeof verifyInviteSchema>;
export type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;
