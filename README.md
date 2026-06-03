# ApplyWise AI

ApplyWise AI is an AI-powered Job Discovery and Application Copilot for software engineering roles.

The product is a Job Intelligence Agent, not an auto-apply bot. It discovers public jobs, scores opportunities against a user's resume, generates draft application materials, and sends recommendations while keeping a human in the loop.

## Current Milestone

Phase 2: project structure.

Included:

- Docker Compose for local services.
- FastAPI backend skeleton.
- FastAPI AI service skeleton.
- APScheduler scheduler skeleton.
- React, TypeScript, and Vite frontend skeleton.
- Health checks and environment examples.

## Human Approval Rules

- The system must never submit job applications automatically.
- The system must never click external apply buttons on behalf of the user.
- Generated content is draft material until the user reviews it.
- Original resumes are never modified.
- Only publicly accessible job listings may be discovered.

## Local Setup

```bash
cp .env.example .env
docker compose up --build
```

Service URLs:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- AI Service: `http://localhost:8001`
- ChromaDB: `http://localhost:8002`
- PostgreSQL: `localhost:5432`

Health checks:

```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/api/v1/heartbeat
```

## Phase 2 Testing Instructions

```bash
docker compose config
python -m compileall services/backend services/ai-service services/scheduler
```

Optional, after Docker is available:

```bash
docker compose up --build
```

## Repository Map

- `docs/`: architecture and roadmap.
- `services/backend/`: public API skeleton.
- `services/ai-service/`: AI workflow skeleton.
- `services/scheduler/`: recurring job skeleton.
- `frontend/`: React dashboard skeleton.
- `packages/`: shared contracts and schemas.
- `infra/`: deployment notes and future infrastructure.
- `scripts/`: local developer helpers.

