import api from "../api/axios";

const parseJwt = (token) => {
  try {
    const payload = token.split(".")[1];
    const base64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    const json = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => `%${`00${c.charCodeAt(0).toString(16)}`.slice(-2)}`)
        .join(""),
    );
    return JSON.parse(json);
  } catch {
    return null;
  }
};

const isTokenExpired = (token) => {
  if (!token) return true;

  const payload = parseJwt(token);
  if (!payload || !payload.exp) return true;

  return Date.now() / 1000 > payload.exp;
};

export const loginUser = async (credentials) => {
  const response = await api.post("/api/token/", credentials);

  localStorage.setItem("access", response.data.access);
  localStorage.setItem("refresh", response.data.refresh);

  return response.data;
};

export const registerUser = async (userData) => {
  return api.post("/api/register/", userData);
};

export const logoutUser = () => {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
};

export const isAuthenticated = () => {
  const token = localStorage.getItem("access");
  return Boolean(token && !isTokenExpired(token));
};
