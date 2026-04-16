import type { AuthCredentials, AuthSession } from "../types/auth";

const BASE_URL = "/api/v1";

async function submitAuth(
  path: "/auth/login" | "/auth/register",
  credentials: AuthCredentials
): Promise<AuthSession> {
  const response = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Auth error ${response.status}: ${detail}`);
  }

  return response.json() as Promise<AuthSession>;
}

export function login(credentials: AuthCredentials): Promise<AuthSession> {
  return submitAuth("/auth/login", credentials);
}

export function register(credentials: AuthCredentials): Promise<AuthSession> {
  return submitAuth("/auth/register", credentials);
}
