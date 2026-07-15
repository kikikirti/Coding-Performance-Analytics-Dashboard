import axios from "axios";

const api = axios.create({
  baseURL:
    import.meta.env.VITE_API_BASE_URL ||
    "http://127.0.0.1:5000",

  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },

  timeout: 15000,
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("authToken");

    if (token) {
      config.headers["Authentication-Token"] = token;
    }

    return config;
  },

  (error) => Promise.reject(error),
);

api.interceptors.response.use(
  (response) => response,

  (error) => {
    const status = error.response?.status;
    const requestUrl = error.config?.url || "";

    const isAuthenticationRequest =
      requestUrl.includes("/login") ||
      requestUrl.includes("/register");

    if (status === 401 && !isAuthenticationRequest) {
      localStorage.removeItem("authToken");
      localStorage.removeItem("authUser");

      if (window.location.pathname !== "/login") {
        window.location.assign("/login");
      }
    }

    return Promise.reject(error);
  },
);

export default api;