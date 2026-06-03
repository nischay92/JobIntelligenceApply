# System Architecture

## Overview

ApplyWise AI is a microservice SaaS platform for job intelligence, recommendation, and human-approved application support.

The system contains:

- Frontend Service: React, TypeScript, Vite dashboard.
- Backend API Service: FastAPI public API, authentication, user data, job management, notifications, authorization, and orchestration.
- AI Service: FastAPI service for resume parsing, job description parsing, match scoring, and generation through an LLM provider abstraction.
- Scheduler Service: APScheduler workers for hourly discovery, digest generation, retries, and summaries.
- PostgreSQL: Primary relational database.
- ChromaDB: Vector database for semantic search over resumes, jobs, and generated content.
- External Providers: Google OAuth, public job board sources, LLM providers, and notification channels.

## High-Level Data Flow

1. User signs in with Google OAuth.
2. User uploads a resume in PDF or DOCX format.
3. Backend stores the original file metadata and sends the file to the AI Service for parsing.
4. AI Service extracts structured resume data, generates embeddings, and stores semantic vectors in ChromaDB.
5. Scheduler discovers public job listings from supported sources.
6. Backend persists normalized job records.
7. AI Service parses job descriptions and generates job embeddings.
8. Match scoring compares resume data and job data.
9. Backend ranks and stores matches.
10. Scheduler sends hourly recommendations through user-approved notification channels.
11. User reviews jobs, generated answers, cover letters, and outreach messages in the dashboard.
12. User manually applies outside the system or uses generated content after review.

## Service Boundaries

### Frontend Service

Responsibilities:

- Dashboard, jobs, job details, resume, settings, and notifications pages.
- Search, filters, saved jobs, charts, dark mode, and responsive layout.
- Clear review workflows for generated application content.
- No direct access to databases, vector stores, or external provider secrets.

### Backend API Service

Responsibilities:

- Authentication and session management.
- Authorization and tenant ownership checks.
- Resume upload metadata and file validation.
- Job CRUD and saved jobs.
- Match records and generated answer storage.
- Notification preferences.
- API rate limiting and request validation.
- Orchestration between frontend, AI Service, Scheduler, PostgreSQL, and ChromaDB.

### AI Service

Responsibilities:

- Resume parsing.
- Job description parsing.
- Match scoring.
- Application material generation.
- Embedding generation.
- Provider abstraction for OpenAI, Claude, and Gemini.

Provider interface:

```text
LLMProvider
  generate(prompt, schema, options)
  embed(input, options)
```

The concrete provider is selected by environment configuration and can be swapped without changing API contracts.

### Scheduler Service

Responsibilities:

- Hourly public job discovery.
- Daily digest preparation.
- Weekly summary preparation.
- Retry failed discovery, parsing, scoring, and notification tasks.
- Persist processing history and failure details.

### Database Service

Responsibilities:

- Durable relational storage for users, resumes, jobs, matches, generated content, notifications, saved jobs, and preferences.
- Transactional integrity.
- Indexing for dashboard and scheduler workloads.

### Vector Database Service

Responsibilities:

- Store embeddings for resumes, jobs, and generated content.
- Enable semantic search and similarity matching.
- Keep vector metadata linked to PostgreSQL records.

## Job Discovery Sources

Supported public sources:

- Greenhouse public boards.
- Lever public postings.
- Ashby public boards.
- Wellfound public pages or APIs where allowed.
- YC Jobs public listings.
- Company career pages.
- RSS feeds where available.

Discovery constraints:

- Use public endpoints and pages only.
- Do not bypass authentication.
- Do not scrape logged-in LinkedIn pages.
- Do not automate LinkedIn applications.
- Do not auto-submit applications.
- Respect rate limits, robots, and provider terms.

## Security Model

- Secrets are loaded from environment variables and never committed.
- Uploaded files are validated by MIME type, extension, size, and parser safety rules.
- User data is tenant-scoped by `user_id`.
- API routes require authentication except health checks and OAuth callbacks.
- Rate limiting is applied to authentication, upload, generation, and discovery-trigger endpoints.
- Generated content is explicitly labeled as draft material.
- Application-related actions require human confirmation and cannot execute external submissions.

## Human-In-The-Loop Model

ApplyWise AI may:

- Discover jobs.
- Score jobs.
- Generate suggestions.
- Draft cover letters and answers.
- Draft recruiter and LinkedIn outreach text.
- Send job recommendations.

ApplyWise AI must not:

- Submit job applications.
- Click external apply buttons on behalf of the user.
- Modify the original resume.
- Send outreach messages without explicit user approval.
- Represent generated content as final without review.

## Deployment Architecture

Local development uses Docker Compose with:

- `frontend`
- `backend`
- `ai-service`
- `scheduler`
- `postgres`
- `chromadb`

Production can deploy the same service boundaries to a container platform. Recommended production additions:

- Managed PostgreSQL.
- Persistent object storage for uploaded files.
- Managed secrets.
- Observability stack.
- Background queue if scheduler workload grows beyond APScheduler.
- CDN for frontend assets.

## Future Scalability

The architecture leaves room for:

- Multiple resumes per user.
- Multiple job board connectors.
- Referral tracking.
- Interview tracking.
- Application tracking.
- Browser extension or autofill assistant with user approval.
- Team collaboration.
- Subscription plans.
- Queue-backed distributed processing.
