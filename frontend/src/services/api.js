import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// ==========================================
// REQUEST INTERCEPTOR
// ==========================================

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// ==========================================
// RESPONSE INTERCEPTOR
// ==========================================

api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {

    const status = error.response?.status;
    const requestUrl = error.config?.url || "";

    // ==========================================
    // 401 FROM LOGIN SHOULD NOT REDIRECT
    // ==========================================
    //
    // Login can return 401 for:
    // - Invalid CAPTCHA
    // - Invalid email
    // - Invalid password
    //
    // Login.jsx needs to receive these errors
    // so it can display the correct message and
    // generate a new CAPTCHA.
    //

    const isLoginRequest =
      requestUrl.includes("/auth/login");

    if (status === 401 && !isLoginRequest) {

      localStorage.removeItem("token");
      localStorage.removeItem("user");
      localStorage.removeItem("role");
      localStorage.removeItem("username");

      window.location.href = "/login";
    }

    return Promise.reject(error);
  }
);

export default api;