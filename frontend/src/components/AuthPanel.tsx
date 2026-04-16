import { FormEvent, useState } from "react";
import { login, register } from "../api/auth";
import type { AuthSession } from "../types/auth";

interface Props {
  onAuthenticated: (session: AuthSession) => void;
}

type AuthMode = "login" | "register";

export function AuthPanel({ onAuthenticated }: Props) {
  const [mode, setMode] = useState<AuthMode>("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      const credentials = { username, password };
      const session = mode === "login" ? await login(credentials) : await register(credentials);
      onAuthenticated(session);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    } finally {
      setSubmitting(false);
    }
  }

  const isLogin = mode === "login";

  return (
    <main className="auth-shell">
      <section className="auth-panel">
        <p className="eyebrow">Invoice Ledger</p>
        <h1>{isLogin ? "Log in" : "Create account"}</h1>
        <p className="auth-copy">
          Use a username and password to access the invoice ledger.
        </p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Username
            <input
              autoComplete="username"
              minLength={3}
              maxLength={40}
              pattern="[A-Za-z0-9_.-]+"
              required
              value={username}
              onChange={(event) => setUsername(event.target.value)}
            />
          </label>

          <label>
            Password
            <input
              autoComplete={isLogin ? "current-password" : "new-password"}
              minLength={8}
              maxLength={128}
              required
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>

          {error && <div className="auth-error">{error}</div>}

          <button className="primary-btn" disabled={submitting} type="submit">
            {submitting ? "Working..." : isLogin ? "Log in" : "Register"}
          </button>
        </form>

        <button
          className="link-btn"
          type="button"
          onClick={() => {
            setError(null);
            setMode(isLogin ? "register" : "login");
          }}
        >
          {isLogin ? "Need an account? Register" : "Already have an account? Log in"}
        </button>
      </section>
    </main>
  );
}
