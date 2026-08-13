import { useCallback } from "react";
import { useAuthStore } from "@/stores/authStore";
import { useLogout } from "@/hooks/useAuthQuery";

/**
 * Convenience hook — replaces the old tRPC-based useAuth.
 * Returns the current user, auth state, and a logout callback.
 */
export function useAuth() {
  const user = useAuthStore((state) => state.user);
  const isLoading = useAuthStore((state) => state.isLoading);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  const logoutMutation = useLogout();
  const logout = useCallback(() => logoutMutation.mutate(), [logoutMutation]);

  return {
    user,
    isLoading,
    isAuthenticated,
    isAdmin: user?.role === "SUPER_ADMIN",
    logout,
  };
}
