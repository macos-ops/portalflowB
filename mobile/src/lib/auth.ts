import * as SecureStore from "expo-secure-store";
import api from "./api";

export type Role = "ADMIN" | "TEAM" | "CLIENT";

export interface Session {
  accessToken: string;
  refreshToken: string;
  role: Role;
}

export async function login(username: string, password: string): Promise<Session> {
  const response = await api.post("/token/", { username, password });
  const { access, refresh } = response.data;

  await SecureStore.setItemAsync("access_token", access);
  await SecureStore.setItemAsync("refresh_token", refresh);

  const role = await fetchRole(access);
  await SecureStore.setItemAsync("role", role);

  return { accessToken: access, refreshToken: refresh, role };
}

async function fetchRole(accessToken: string): Promise<Role> {
  const payload = JSON.parse(atob(accessToken.split(".")[1]));
  return payload.role ?? "CLIENT";
}

export async function logout(): Promise<void> {
  await SecureStore.deleteItemAsync("access_token");
  await SecureStore.deleteItemAsync("refresh_token");
  await SecureStore.deleteItemAsync("role");
}

export async function getSession(): Promise<Session | null> {
  const accessToken = await SecureStore.getItemAsync("access_token");
  const refreshToken = await SecureStore.getItemAsync("refresh_token");
  const role = await SecureStore.getItemAsync("role");

  if (!accessToken || !refreshToken || !role) {
    return null;
  }

  return { accessToken, refreshToken, role: role as Role };
}
