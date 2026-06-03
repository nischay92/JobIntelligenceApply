import { useEffect, useState } from "react";
import {
  Bell,
  BriefcaseBusiness,
  FileText,
  LogIn,
  LogOut,
  ShieldCheck,
  Upload,
  Sparkles
} from "lucide-react";

const milestones = [
  "PDF and DOCX upload",
  "Authenticated resume API",
  "Secure file validation",
  "Resume metadata storage",
  "Human-in-loop guardrails"
];

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

type UserProfile = {
  id: string;
  email: string;
  name: string;
  avatar_url: string | null;
};

type Resume = {
  id: string;
  original_filename: string;
  file_mime_type: string;
  file_size_bytes: number;
  status: string;
  active: boolean;
  created_at: string;
};

export function App() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [authStatus, setAuthStatus] = useState<"checking" | "anonymous" | "authenticated">(
    "checking"
  );
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "uploaded">("idle");
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
        await loadResumes();
      } catch {
        setError("The backend is not reachable yet.");
        setAuthStatus("anonymous");
      }
    }

    void loadUser();
  }, []);

  async function loadResumes() {
    const response = await fetch(`${apiBaseUrl}/api/v1/resumes`, {
      credentials: "include"
    });
    if (response.ok) {
      setResumes((await response.json()) as Resume[]);
    }
  }

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
    setResumes([]);
    setAuthStatus("anonymous");
  }

  async function uploadResume() {
    if (!selectedFile) {
      setError("Choose a PDF or DOCX resume first.");
      return;
    }

    setError(null);
    setUploadStatus("uploading");
    const formData = new FormData();
    formData.append("file", selectedFile);

    const response = await fetch(`${apiBaseUrl}/api/v1/resumes`, {
      method: "POST",
      credentials: "include",
      body: formData
    });

    if (!response.ok) {
      const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
      setError(payload?.detail ?? "Resume upload failed.");
      setUploadStatus("idle");
      return;
    }

    setSelectedFile(null);
    setUploadStatus("uploaded");
    await loadResumes();
  }

  return (
    <main className="app-shell">
      <section className="intro">
        <div>
          <p className="eyebrow">ApplyWise AI</p>
          <h1>Job intelligence with the human firmly in charge.</h1>
          <p className="summary">
            Phase 4 adds authenticated resume upload for PDF and DOCX files. Original resumes are
            stored safely as source documents; parsing and suggestions come in later phases.
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

      {authStatus === "authenticated" ? (
        <section className="resume-workbench" aria-label="Resume upload">
          <div>
            <p className="eyebrow">Resume</p>
            <h2>Upload your source resume.</h2>
            <p>
              Files are accepted as PDF or DOCX and stored unchanged. ApplyWise will use parsed
              copies and suggestions later without editing this original.
            </p>
          </div>
          <div className="upload-panel">
            <label className="file-picker">
              <FileText aria-hidden="true" />
              <span>{selectedFile ? selectedFile.name : "Choose PDF or DOCX"}</span>
              <input
                accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
                type="file"
              />
            </label>
            <button
              className="auth-button"
              disabled={uploadStatus === "uploading"}
              onClick={() => void uploadResume()}
              type="button"
            >
              <Upload aria-hidden="true" />
              <span>{uploadStatus === "uploading" ? "Uploading" : "Upload resume"}</span>
            </button>
            {uploadStatus === "uploaded" ? <p className="auth-note">Resume uploaded.</p> : null}
          </div>
          <div className="resume-list" aria-label="Uploaded resumes">
            {resumes.length === 0 ? (
              <p>No resumes uploaded yet.</p>
            ) : (
              resumes.map((resume) => (
                <article className="resume-row" key={resume.id}>
                  <FileText aria-hidden="true" />
                  <div>
                    <strong>{resume.original_filename}</strong>
                    <span>
                      {resume.status} · {Math.ceil(resume.file_size_bytes / 1024)} KB
                      {resume.active ? " · active" : ""}
                    </span>
                  </div>
                </article>
              ))
            )}
          </div>
        </section>
      ) : null}

      <section className="milestone-grid" aria-label="Phase 4 milestones">
        {milestones.map((milestone) => (
          <article className="milestone-card" key={milestone}>
            <Sparkles aria-hidden="true" />
            <span>{milestone}</span>
          </article>
        ))}
      </section>

      <footer className="footer-note">
        <Bell aria-hidden="true" />
        <span>Resume parsing arrives in Phase 5; this phase only stores source resumes.</span>
      </footer>
    </main>
  );
}
