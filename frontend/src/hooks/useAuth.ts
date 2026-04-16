import { useMemo, useState } from "react";
import type { AuthSession } from "../types/auth";

const STORAGE_KEY = "invoice-ledger-session";

function readStoredSession(): AuthSession | null {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;

  try {
    return JSON.parse(raw) as AuthSession;
  } catch {
    localStorage.removeItem(STORAGE_KEY);
    return null;
  }
}

export function useAuth() {
  const [session, setSessionState] = useState<AuthSession | null>(() => readStoredSession());

  function setSession(nextSession: AuthSession) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(nextSession));
    setSessionState(nextSession);
  }

  function logout() {
    localStorage.removeItem(STORAGE_KEY);
    setSessionState(null);
  }

  return useMemo(
    () => ({
      session,
      token: session?.access_token ?? null,
      user: session?.user ?? null,
      setSession,
      logout,
    }),
    [session]
  );
}
