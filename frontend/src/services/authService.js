import api from "../api/api";

/*
|--------------------------------------------------------------------------
| Authentication
|--------------------------------------------------------------------------
*/

export const login = async (email, password) => {
  const response = await api.post("/auth/login", {
    email,
    password,
  });

  return response.data;
};

export const register = async (userData) => {
  const response = await api.post("/auth/register", userData);

  return response.data;
};

export const verifyEmail = async (token) => {
  const response = await api.get("/auth/verify-email", {
    params: {
      token,
    },
  });

  return response.data;
};

export const resendVerification = async (email) => {
  const response = await api.post("/auth/resend-verification", {
    email,
  });

  return response.data;
};

/*
|--------------------------------------------------------------------------
| Password Reset
|--------------------------------------------------------------------------
*/

export const forgotPassword = async (email) => {
  const response = await api.post("/auth/forgot-password", {
    email,
  });

  return response.data;
};

export const resetPassword = async (token, password) => {
  const response = await api.post("/auth/reset-password", {
    token,
    password,
  });

  return response.data;
};

/*
|--------------------------------------------------------------------------
| Current User
|--------------------------------------------------------------------------
*/

export const getCurrentUser = async () => {
  const response = await api.get("/auth/me");

  return response.data;
};

/*
|--------------------------------------------------------------------------
| Logout
|--------------------------------------------------------------------------
*/

export const logout = () => {
  localStorage.removeItem("access_token");
};
