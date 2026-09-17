import axios from "axios";
import * as SecureStore from "expo-secure-store";

const API_BASE_URL = "https://portalflowb-production.up.railway.app/api";

export const api = axios.create({
  baseURL: API_BASE_URL,
});

// Attach the access token to every request automatically, if one exists
api.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
