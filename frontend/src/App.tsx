import { useEffect, useState } from "react";
import {
  Bell,
  BriefcaseBusiness,
  FileText,
  LogIn,
  LogOut,
  ShieldCheck,
  Sparkles
} from "lucide-react";

const milestones = [
  "Google OAuth routes",
  "Signed session cookie",
  "User profile persistence",
  "Protected /me endpoint",
  "Human-in-loop guardrails"
];

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

type UserProfile = {
  id: string;
  email: string;
  name: string;
  avatar_url: string | null;
};

export function App() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [authStatus, setAuthStatus] = useState<"checking" | "anonymous" | "authenticated">(
    "checking"
  );
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadUser() {
      try {
        const response = await fetch(`${apiBaseUrl}/api/v1/auth/me`, {
          credentials: "include"
        });
        if (response.status === 401) {
          setAuthStatus("anonymous");
          return;
        }
        if (!response.ok) {
          throw new Error("Unable to load your session.");
        }
        const profile = (await response.json()) as UserProfile;
        setUser(profile);
        setAuthStatus("authenticated");
      } catch {
        setError("The backend is not reachable yet.");
        setAuthStatus("anonymous");
      }
    }

    void loadUser();
  }, []);

  async function signIn() {
    setError(null);
    const response = await fetch(`${apiBaseUrl}/api/v1/auth/google/login`, {
      credentials: "include"
    });
    if (!response.ok) {
      setError("Google OAuth is not configured or the backend is unavailable.");
      return;
    }
    const payload = (await response.json()) as { authorization_url: string };
    window.location.assign(payload.authorization_url);
  }

  async function signOut() {
    await fetch(`${apiBaseUrl}/api/v1/auth/logout`, {
      method: "POST",
      credentials: "include"
    });
    setUser(null);
    setAuthStatus("anonymous");
  }

  return (
    <main className="app-shell">
      <section className="intro">
        <div>
          <p className="eyebrow">ApplyWise AI</p>
          <h1>Job intelligence with the human firmly in charge.</h1>
          <p className="summary">
            Phase 3 adds Google authentication, signed sessions, and a protected identity
            endpoint without changing the product rule: ApplyWise AI never submits applications.
          </p>
        </div>
        <div className="status-panel" aria-label="Authentication status">
          {authStatus === "authenticated" && user ? (
            <>
              <div className="profile-row">
                {user.avatar_url ? <img alt="" src={user.avatar_url} /> : null}
                <div>
                  <strong>{user.name}</strong>
                  <span>{user.email}</span>
                </div>
              </div>
              <button className="auth-button secondary" onClick={() => void signOut()} type="button">
                <LogOut aria-hidden="true" />
                <span>Sign out</span>
              </button>
            </>
          ) : (
            <>
              <button className="auth-button" onClick={() => void signIn()} type="button">
                <LogIn aria-hidden="true" />
                <span>Sign in with Google</span>
              </button>
              <p className="auth-note">
                {authStatus === "checking" ? "Checking current session." : "Authentication is ready."}
              </p>
            </>
          )}
          {error ? <p className="error-note">{error}</p> : null}
          <div className="status-row">
            <ShieldCheck aria-hidden="true" />
            <span>No auto-submit workflows</span>
          </div>
          <div className="status-row">
            <BriefcaseBusiness aria-hidden="true" />
            <span>Public job discovery only</span>
          </div>
          <div className="status-row">
            <FileText aria-hidden="true" />
            <span>Original resumes stay untouched</span>
          </div>
        </div>
      </section>

      <section className="milestone-grid" aria-label="Phase 3 milestones">
        {milestones.map((milestone) => (
          <article className="milestone-card" key={milestone}>
            <Sparkles aria-hidden="true" />
            <span>{milestone}</span>
          </article>
        ))}
      </section>

      <footer className="footer-note">
        <Bell aria-hidden="true" />
        <span>Dashboard features arrive in Phase 10; this screen is the authenticated shell.</span>
      </footer>
    </main>
  );
}
