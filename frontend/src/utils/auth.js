export const getToken = () => {
  return (
    localStorage.getItem("access_token") ||
    sessionStorage.getItem("access_token")
  );
};

export const isAuthenticated = () => {
  return !!getToken();
};

export const logout = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user");

  sessionStorage.removeItem("access_token");
  sessionStorage.removeItem("user");
};

export const getCurrentUser = () => {
  const user =
    localStorage.getItem("user") ||
    sessionStorage.getItem("user");

  if (!user) return null;

  try {
    return JSON.parse(user);
  } catch (error) {
    return null;
  }
};

export const getUserRole = () => {
  const user = getCurrentUser();
  return user?.role || null;
};

export const isSystemAdmin = () => {
  const role = getUserRole();

  return (
    role === "SystemAdmin" ||
    role === "SYSTEM_ADMIN"
  );
};

export const isInstitutionAdmin = () => {
  const role = getUserRole();

  return (
    role === "InstitutionAdmin" ||
    role === "INSTITUTION_ADMIN"
  );
};

export const isResearcher = () => {
  const role = getUserRole();

  return (
    role === "Researcher" ||
    role === "RESEARCHER"
  );
};

export const isAdmin = () => {
  return (
    isSystemAdmin() ||
    isInstitutionAdmin()
  );
};

export const isLoggedIn = () => {
  return !!(
    localStorage.getItem("access_token") ||
    sessionStorage.getItem("access_token")
  );
};