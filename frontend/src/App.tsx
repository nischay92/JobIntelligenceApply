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
  "Local PDF/DOCX parsing",
  "Structured profile JSON",
  "Deterministic embeddings",
  "Parsed resume storage",
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
  parsed_profile: {
    skills?: string[];
    keywords?: string[];
  } | null;
  parser_version: string | null;
  parse_error: string | null;
  created_at: string;
};

type Job = {
  id: string;
  company: string;
  title: string;
  location: string | null;
  source: string;
  remote_policy: string;
  description_url: string;
};

export function App() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [authStatus, setAuthStatus] = useState<"checking" | "anonymous" | "authenticated">(
    "checking"
  );
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "uploaded">("idle");
  const [parsingId, setParsingId] = useState<string | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [discoveryStatus, setDiscoveryStatus] = useState<"idle" | "running" | "done">("idle");
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
        await loadJobs();
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

  async function loadJobs() {
    const response = await fetch(`${apiBaseUrl}/api/v1/jobs`, {
      credentials: "include"
    });
    if (response.ok) {
      setJobs((await response.json()) as Job[]);
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
    setJobs([]);
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

  async function parseResume(resumeId: string) {
    setError(null);
    setParsingId(resumeId);
    const response = await fetch(`${apiBaseUrl}/api/v1/resumes/${resumeId}/parse`, {
      method: "POST",
      credentials: "include"
    });

    if (!response.ok) {
      const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
      setError(payload?.detail ?? "Resume parsing failed.");
      setParsingId(null);
      return;
    }

    setParsingId(null);
    await loadResumes();
  }

  async function runSampleDiscovery() {
    setError(null);
    setDiscoveryStatus("running");
    const response = await fetch(`${apiBaseUrl}/api/v1/jobs/discovery-runs`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source: "sample", company: "ApplyWise Demo Co", limit: 5 })
    });

    if (!response.ok) {
      const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
      setError(payload?.detail ?? "Job discovery failed.");
      setDiscoveryStatus("idle");
      return;
    }

    setDiscoveryStatus("done");
    await loadJobs();
  }

  return (
    <main className="app-shell">
      <section className="intro">
        <div>
          <p className="eyebrow">ApplyWise AI</p>
          <h1>Job intelligence with the human firmly in charge.</h1>
          <p className="summary">
            Phase 5 parses uploaded resumes into structured profile JSON and deterministic
            embeddings. Source resumes stay unchanged.
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
                    {resume.parsed_profile?.skills?.length ? (
                      <small>{resume.parsed_profile.skills.slice(0, 6).join(", ")}</small>
                    ) : null}
                  </div>
                  <button
                    className="icon-action"
                    disabled={parsingId === resume.id || resume.status === "parsed"}
                    onClick={() => void parseResume(resume.id)}
                    title="Parse resume"
                    type="button"
                  >
                    <Sparkles aria-hidden="true" />
                  </button>
                </article>
              ))
            )}
          </div>
        </section>
      ) : null}

      {authStatus === "authenticated" ? (
        <section className="jobs-workbench" aria-label="Job discovery">
          <div>
            <p className="eyebrow">Jobs</p>
            <h2>Discover public roles.</h2>
            <p>
              Discovery uses public job board endpoints only. ApplyWise shows direct links for human
              review and never submits applications.
            </p>
          </div>
          <button
            className="auth-button"
            disabled={discoveryStatus === "running"}
            onClick={() => void runSampleDiscovery()}
            type="button"
          >
            <BriefcaseBusiness aria-hidden="true" />
            <span>{discoveryStatus === "running" ? "Discovering" : "Run sample discovery"}</span>
          </button>
          <div className="job-list" aria-label="Discovered jobs">
            {jobs.length === 0 ? (
              <p>No jobs discovered yet.</p>
            ) : (
              jobs.slice(0, 5).map((job) => (
                <article className="job-row" key={job.id}>
                  <BriefcaseBusiness aria-hidden="true" />
                  <div>
                    <strong>{job.company}</strong>
                    <span>
                      {job.title} · {job.location ?? "Location not listed"} · {job.remote_policy}
                    </span>
                  </div>
                </article>
              ))
            )}
          </div>
        </section>
      ) : null}

      <section className="milestone-grid" aria-label="Phase 5 milestones">
        {milestones.map((milestone) => (
          <article className="milestone-card" key={milestone}>
            <Sparkles aria-hidden="true" />
            <span>{milestone}</span>
          </article>
        ))}
      </section>

      <footer className="footer-note">
        <Bell aria-hidden="true" />
        <span>Application content generation waits for Phase 8 and always requires review.</span>
      </footer>
    </main>
  );
}
