# Project Roadmap

ApplyWise AI will be built incrementally. Each phase ends with generated code or documentation, testing instructions, a Git commit, and a stop for approval.

## Phase 1: Architecture and Roadmap

Deliverables:

- System architecture.
- Folder structure.
- Database schema.
- ER diagram.
- API design.
- Project roadmap.

Commit:

```bash
git commit -m "docs: architecture and roadmap"
```

Stop for approval before Phase 2.

## Phase 2: Project Structure

Deliverables:

- Docker Compose.
- Backend skeleton.
- Frontend skeleton.
- AI Service skeleton.
- Scheduler skeleton.
- Environment example files.
- Basic health checks.

Commit:

```bash
git commit -m "feat: initialize project structure"
```

Credential stop:

- PostgreSQL credentials are represented as local development variables in `.env.example`.
- No real secrets are required or committed.

## Phase 3: Authentication

Deliverables:

- Google OAuth flow.
- User profile persistence.
- Authenticated session support.
- Protected API routes.
- Frontend sign-in and sign-out flow.

Commit:

```bash
git commit -m "feat: implement authentication"
```

Credential stop:

- Google OAuth client ID.
- Google OAuth client secret.
- OAuth redirect URI.
- Session secret.

## Phase 4: Resume Upload

Deliverables:

- PDF and DOCX upload API.
- File validation.
- Secure storage path handling.
- Resume list and details APIs.
- Resume upload UI.

Commit:

```bash
git commit -m "feat: add resume upload"
```

## Phase 5: Resume Parsing

Deliverables:

- Resume text extraction.
- Structured resume JSON.
- Resume parser API integration.
- Embedding generation.
- ChromaDB storage.
- Parser tests.

Commit:

```bash
git commit -m "feat: implement resume parsing"
```

Credential stop:

- OpenAI, Claude, or Gemini API credentials are required before live LLM parsing.
- The provider can run in mock mode for local tests.

## Phase 6: Job Discovery

Deliverables:

- Public connectors for Greenhouse, Lever, Ashby, Wellfound, YC Jobs, RSS, and company pages.
- Scheduler discovery jobs.
- Job normalization.
- Duplicate prevention.
- Discovery history.

Commit:

```bash
git commit -m "feat: implement job discovery"
```

Compliance stop:

- Confirm target sources are public and allowed.
- No logged-in LinkedIn scraping.
- No authentication bypassing.

## Phase 7: Match Scoring

Deliverables:

- Resume-to-job scoring.
- Skill, experience, and education sub-scores.
- Missing skills and keywords.
- Priority calculation.
- Match explanation.
- Match APIs and tests.

Commit:

```bash
git commit -m "feat: implement job scoring"
```

## Phase 8: Application Assistant

Deliverables:

- Tailored resume suggestions.
- Missing keyword suggestions.
- Cover letter drafts.
- Recruiter outreach email drafts.
- LinkedIn outreach message drafts.
- Application question answer drafts.
- Human review states.

Commit:

```bash
git commit -m "feat: implement application assistant"
```

Product stop:

- Confirm no generated content is submitted or sent externally without explicit approval.
- Confirm original resumes remain unchanged.

## Phase 9: Hourly Digests

Deliverables:

- Hourly top 5 job digest.
- Daily digest.
- Weekly summary.
- Email, Telegram, and Discord channel abstractions.
- Notification preferences.
- Delivery history and retry handling.

Commit:

```bash
git commit -m "feat: implement notification system"
```

Credential stop:

- Email provider credentials.
- Telegram bot token and chat configuration.
- Discord webhook or bot credentials.

## Phase 10: Dashboard

Deliverables:

- Dashboard page.
- Jobs page.
- Job details page.
- Resume page.
- Settings page.
- Notifications page.
- Search, filters, dark mode, saved jobs, charts, and responsive layout.

Commit:

```bash
git commit -m "feat: build dashboard"
```

## Phase 11: Production Hardening

Deliverables:

- Production Docker settings.
- Health checks.
- Structured logging.
- Observability hooks.
- Rate limiting.
- Input validation audit.
- Upload security audit.
- CI test commands.
- Deployment documentation.

Commit:

```bash
git commit -m "feat: production readiness"
```

## Release Readiness Checklist

- No secrets committed.
- `.env.example` documents all configuration.
- All routes requiring user data are authenticated.
- Uploaded files are validated and isolated.
- Application submissions are not automated.
- Generated content is stored separately from original resumes.
- Public job source compliance is documented.
- Backend tests pass.
- Frontend tests pass.
- Docker Compose starts core services.
- Health checks pass.
- Dashboard is responsive.
- Recruiter-demo flow is polished.
