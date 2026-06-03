# Folder Structure

The project will use a monorepo so shared contracts, local orchestration, and documentation evolve together.

```text
applywise-ai/
  README.md
  .env.example
  docker-compose.yml
  docs/
    README.md
    architecture.md
    folder-structure.md
    database-schema.md
    er-diagram.md
    api-design.md
    roadmap.md
  services/
    backend/
      app/
        api/
          v1/
            auth.py
            resumes.py
            jobs.py
            matches.py
            generated_answers.py
            notifications.py
            preferences.py
        core/
          config.py
          security.py
          rate_limit.py
        db/
          session.py
          models/
          repositories/
        schemas/
        services/
        main.py
      alembic/
      tests/
      Dockerfile
      pyproject.toml
    ai-service/
      app/
        api/
          v1/
            resumes.py
            jobs.py
            scoring.py
            generation.py
            embeddings.py
        core/
          config.py
        providers/
          base.py
          openai_provider.py
          claude_provider.py
          gemini_provider.py
        parsers/
        scoring/
        generation/
        vectorstore/
        main.py
      tests/
      Dockerfile
      pyproject.toml
    scheduler/
      app/
        core/
          config.py
        jobs/
          discovery.py
          digests.py
          retries.py
          summaries.py
        connectors/
          greenhouse.py
          lever.py
          ashby.py
          wellfound.py
          yc_jobs.py
          rss.py
          company_pages.py
        main.py
      tests/
      Dockerfile
      pyproject.toml
  frontend/
    src/
      app/
      components/
      features/
        dashboard/
        jobs/
        job-details/
        resume/
        settings/
        notifications/
      lib/
      routes/
      styles/
      tests/
    public/
    Dockerfile
    package.json
    vite.config.ts
  packages/
    api-contracts/
      openapi/
      schemas/
    shared-types/
  infra/
    local/
    production/
  scripts/
    dev/
    ci/
```

## Ownership

- `docs/`: product, architecture, API, data model, and roadmap decisions.
- `services/backend/`: user-facing REST APIs and relational persistence.
- `services/ai-service/`: AI workflows, parsing, scoring, generation, embeddings, and provider abstraction.
- `services/scheduler/`: recurring discovery, digest, retry, and summary workflows.
- `frontend/`: user dashboard and review experience.
- `packages/`: shared schemas and API contracts.
- `infra/`: deployment and environment configuration.
- `scripts/`: local development and CI helpers.

## Milestone Mapping

- Phase 1: `docs/`
- Phase 2: service skeletons, Dockerfiles, compose, and environment examples.
- Phase 3: backend authentication and frontend auth flow.
- Phase 4: resume upload APIs and UI.
- Phase 5: AI parsing and embedding pipeline.
- Phase 6: job discovery connectors and scheduler jobs.
- Phase 7: match scoring pipeline.
- Phase 8: generated application support materials.
- Phase 9: notification channels and digests.
- Phase 10: full dashboard experience.
- Phase 11: production hardening.
