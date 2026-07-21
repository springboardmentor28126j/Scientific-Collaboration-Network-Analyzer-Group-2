import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router";
import { getMe, login, forgotPassword, resetPassword, verifyEmail, verifyInvite } from "@/api/auth";
import { registerInstitution, listInstitutions, activateInstitution, deactivateInstitution } from "@/api/institution";
import { createInstitutionUser, listInstitutionUsers, activateUser, deactivateUser } from "@/api/user";
import { useAuthStore } from "@/stores/authStore";
import { toast } from "sonner";
import type { UserMe, Institution, InstitutionUser } from "@/types";

// Auth Queries
export function useMe() {
  const { isAuthenticated } = useAuthStore();

  return useQuery<UserMe>({
    queryKey: ["me"],
    queryFn: () => getMe(),
    enabled: isAuthenticated,
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: false,
  });
}

export function useLogin() {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: ({ username, password }: { username: string; password: string }) =>
      login(username, password),
    onSuccess: async (data) => {
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      try {
        const user = await getMe();
        useAuthStore.getState().login(data.access_token, data.refresh_token, user);
        toast.success("Login successful!");
        navigate("/dashboard");
      } catch {
        toast.error("Failed to fetch user data");
      }
    },
    onError: (error: Error) => {
      toast.error(error.message || "Login failed");
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: async () => {
      useAuthStore.getState().logout();
    },
    onSuccess: () => {
      queryClient.clear();
      navigate("/login");
      toast.success("Logged out successfully");
    },
  });
}

export function useForgotPassword() {
  return useMutation({
    mutationFn: (email: string) => forgotPassword(email),
    onSuccess: () => {
      toast.success("If an account exists, a reset link has been sent");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to send reset link");
    },
  });
}

export function useResetPassword() {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: ({ token, new_password }: { token: string; new_password: string }) =>
      resetPassword(token, new_password),
    onSuccess: () => {
      toast.success("Password reset successful! Please login.");
      navigate("/login");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to reset password");
    },
  });
}

export function useVerifyEmail() {
  return useMutation({
    mutationFn: (token: string) => verifyEmail(token),
    onSuccess: () => {
      toast.success("Email verified successfully!");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Verification failed");
    },
  });
}

export function useVerifyInvite() {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: ({ token, password }: { token: string; password: string }) =>
      verifyInvite(token, password),
    onSuccess: () => {
      toast.success("Account activated! Please login.");
      navigate("/login");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Verification failed");
    },
  });
}

// Institution Queries
export function useRegisterInstitution() {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (data: {
      name: string;
      address: string;
      admin_full_name: string;
      admin_email: string;
      admin_password: string;
      logo: File;
    }) => registerInstitution(data),
    onSuccess: () => {
      toast.success("Institution registered! Please check your email to verify.");
      navigate("/login");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Registration failed");
    },
  });
}

export function useInstitutions() {
  return useQuery<Institution[]>({
    queryKey: ["institutions"],
    queryFn: () => listInstitutions(),
    staleTime: 1000 * 30,
  });
}

export function useActivateInstitution() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (institutionId: string) => activateInstitution(institutionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["institutions"] });
      toast.success("Institution activated");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to activate institution");
    },
  });
}

export function useDeactivateInstitution() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (institutionId: string) => deactivateInstitution(institutionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["institutions"] });
      toast.success("Institution deactivated");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to deactivate institution");
    },
  });
}

// Institution User Queries
export function useInstitutionUsers(role?: "RESEARCHER" | "REVIEWER") {
  return useQuery<InstitutionUser[]>({
    queryKey: ["institution-users", role],
    queryFn: () => listInstitutionUsers(role),
    staleTime: 1000 * 30,
  });
}

export function useCreateInstitutionUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      email: string;
      full_name: string;
      role: "RESEARCHER" | "REVIEWER";
      description?: string;
    }) => createInstitutionUser(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["institution-users"] });
      toast.success("User created and invite sent!");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to create user");
    },
  });
}

export function useActivateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: string) => activateUser(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["institution-users"] });
      toast.success("User activated");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to activate user");
    },
  });
}

export function useDeactivateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: string) => deactivateUser(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["institution-users"] });
      toast.success("User deactivated");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to deactivate user");
    },
  });
}
