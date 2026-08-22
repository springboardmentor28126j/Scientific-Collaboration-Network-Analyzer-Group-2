import { useEffect } from "react";
import { useAuthStore } from "@/stores/authStore";
import { getMe } from "@/api/auth";

export function useAuthInit() {
  const { isAuthenticated, setUser, setLoading, logout } = useAuthStore();

  useEffect(() => {
    async function init() {
      const token = localStorage.getItem("access_token");
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const user = await getMe();
        setUser(user);
      } catch {
        logout();
      } finally {
        setLoading(false);
      }
    }

    init();
  }, [setUser, setLoading, logout]);

  return { isAuthenticated };
}
