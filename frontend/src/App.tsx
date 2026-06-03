import { Bell, BriefcaseBusiness, FileText, ShieldCheck, Sparkles } from "lucide-react";

const milestones = [
  "Backend API skeleton",
  "AI Service skeleton",
  "Scheduler skeleton",
  "Frontend skeleton",
  "Docker Compose orchestration"
];

export function App() {
  return (
    <main className="app-shell">
      <section className="intro">
        <div>
          <p className="eyebrow">ApplyWise AI</p>
          <h1>Job intelligence with the human firmly in charge.</h1>
          <p className="summary">
            Phase 2 initializes the production-shaped service skeleton for a public job
            discovery, resume intelligence, scoring, and recommendation platform.
          </p>
        </div>
        <div className="status-panel" aria-label="Phase 2 service status">
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

      <section className="milestone-grid" aria-label="Phase 2 milestones">
        {milestones.map((milestone) => (
          <article className="milestone-card" key={milestone}>
            <Sparkles aria-hidden="true" />
            <span>{milestone}</span>
          </article>
        ))}
      </section>

      <footer className="footer-note">
        <Bell aria-hidden="true" />
        <span>Dashboard features arrive in Phase 10; this screen is the service shell.</span>
      </footer>
    </main>
  );
}

