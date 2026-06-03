# ApplyWise AI Documentation

ApplyWise AI is an AI-powered Job Discovery and Application Copilot. It discovers public software engineering opportunities, parses job descriptions, compares them with a user's resume, generates application support materials, and sends recommendations while keeping the user in full control.

ApplyWise AI is not an auto-apply bot. The platform must never submit applications automatically, bypass authentication, scrape private pages, or automate LinkedIn applications.

## Phase 1 Artifacts

- [System Architecture](./architecture.md)
- [Folder Structure](./folder-structure.md)
- [Database Schema](./database-schema.md)
- [ER Diagram](./er-diagram.md)
- [API Design](./api-design.md)
- [Project Roadmap](./roadmap.md)

## Product Guardrails

- Human approval is mandatory before any application-related workflow.
- Generated resumes, cover letters, outreach messages, and answers are saved as suggestions only.
- The user's original resume is never modified.
- Job discovery only uses publicly accessible sources and official/public job board APIs where available.
- The system must honor robots, terms, rate limits, and authentication boundaries.
- LinkedIn application submission and logged-in scraping are explicitly out of scope.

## Phase 1 Testing Instructions

Phase 1 is documentation-only. Verify with:

```bash
git status --short
find docs -maxdepth 1 -type f | sort
```

Confirm the docs include:

- System architecture
- Folder structure
- Database schema
- ER diagram
- API design
- Project roadmap
- Human-in-the-loop and no-auto-submit constraints

## Phase 1 Commit

```bash
git commit -m "docs: architecture and roadmap"
```
