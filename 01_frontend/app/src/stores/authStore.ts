import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { UserMe, UserRole } from "@/types";

interface AuthState {
  user: UserMe | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // Actions
  setUser: (user: UserMe | null) => void;
  setTokens: (accessToken: string | null, refreshToken: string | null) => void;
  setLoading: (loading: boolean) => void;
  login: (accessToken: string, refreshToken: string, user: UserMe) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: true,

      setUser: (user) =>
        set({ user, isAuthenticated: !!user }),

      setTokens: (accessToken, refreshToken) =>
        set({ accessToken, refreshToken }),

      setLoading: (loading) => set({ isLoading: loading }),

      login: (accessToken, refreshToken, user) => {
        localStorage.setItem("access_token", accessToken);
        localStorage.setItem("refresh_token", refreshToken);
        set({ accessToken, refreshToken, user, isAuthenticated: true });
      },

      logout: () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        set({
          accessToken: null,
          refreshToken: null,
          user: null,
          isAuthenticated: false,
        });
      },
    }),
    {
      name: "researchmesh-auth",
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Role-based access helpers
export function useIsSuperAdmin(): boolean {
  const user = useAuthStore((state) => state.user);
  return user?.role === "SUPER_ADMIN";
}

export function useIsInstitutionAdmin(): boolean {
  const user = useAuthStore((state) => state.user);
  return user?.role === "INSTITUTION_ADMIN";
}

export function useIsResearcher(): boolean {
  const user = useAuthStore((state) => state.user);
  return user?.role === "RESEARCHER";
}

export function useIsReviewer(): boolean {
  const user = useAuthStore((state) => state.user);
  return user?.role === "REVIEWER";
}

export function useHasRole(role: UserRole): boolean {
  const user = useAuthStore((state) => state.user);
  return user?.role === role;
}
