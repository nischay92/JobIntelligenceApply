# ER Diagram

```mermaid
erDiagram
  users {
    uuid id PK
    text google_sub UK
    text email UK
    text name
    text avatar_url
    text timezone
    timestamptz created_at
    timestamptz updated_at
  }

  resumes {
    uuid id PK
    uuid user_id FK
    text original_filename
    text file_mime_type
    bigint file_size_bytes
    text storage_path
    text status
    jsonb parsed_profile
    boolean active
    text vector_collection
    text vector_id
    text parse_error
    timestamptz created_at
    timestamptz updated_at
  }

  jobs {
    uuid id PK
    text source
    text external_id
    text company
    text title
    text location
    text employment_type
    integer salary_min
    integer salary_max
    text salary_currency
    text description_url
    text apply_url
    text raw_description
    jsonb parsed_description
    text[] required_skills
    text[] preferred_skills
    text[] technology_stack
    numeric years_experience_min
    numeric years_experience_max
    text[] sponsorship_hints
    boolean security_clearance_required
    text remote_policy
    text status
    text vector_collection
    text vector_id
    timestamptz discovered_at
    timestamptz created_at
    timestamptz updated_at
  }

  job_matches {
    uuid id PK
    uuid user_id FK
    uuid resume_id FK
    uuid job_id FK
    integer overall_score
    integer skill_score
    integer experience_score
    integer education_score
    text[] missing_skills
    text[] missing_keywords
    text[] match_reasons
    text priority
    text priority_reason
    text scoring_model
    timestamptz created_at
    timestamptz updated_at
  }

  generated_answers {
    uuid id PK
    uuid user_id FK
    uuid resume_id FK
    uuid job_id FK
    text content_type
    text prompt_label
    text content
    jsonb metadata
    text status
    text vector_collection
    text vector_id
    timestamptz created_at
    timestamptz updated_at
  }

  notifications {
    uuid id PK
    uuid user_id FK
    text channel
    text notification_type
    text subject
    text body
    text status
    text provider_message_id
    text error
    timestamptz sent_at
    timestamptz created_at
    timestamptz updated_at
  }

  saved_jobs {
    uuid id PK
    uuid user_id FK
    uuid job_id FK
    text notes
    text application_status
    timestamptz created_at
    timestamptz updated_at
  }

  search_preferences {
    uuid id PK
    uuid user_id FK
    text[] target_titles
    text[] target_locations
    text remote_preference
    integer min_salary
    boolean visa_sponsorship_required
    text[] preferred_technologies
    text[] excluded_companies
    text[] notification_channels
    boolean hourly_digest_enabled
    boolean daily_digest_enabled
    boolean weekly_summary_enabled
    timestamptz created_at
    timestamptz updated_at
  }

  processing_runs {
    uuid id PK
    text run_type
    text status
    text source
    timestamptz started_at
    timestamptz finished_at
    integer records_seen
    integer records_created
    integer records_updated
    text error
    jsonb metadata
  }

  users ||--o{ resumes : owns
  users ||--o{ job_matches : receives
  users ||--o{ generated_answers : owns
  users ||--o{ notifications : receives
  users ||--o{ saved_jobs : saves
  users ||--|| search_preferences : configures
  resumes ||--o{ job_matches : scored_against
  jobs ||--o{ job_matches : matched_to
  resumes ||--o{ generated_answers : informs
  jobs ||--o{ generated_answers : targets
  jobs ||--o{ saved_jobs : saved_as
```

## Vector Relationships

ChromaDB stores vectors outside PostgreSQL. PostgreSQL records keep `vector_collection` and `vector_id` references for:

- `resumes`
- `jobs`
- `generated_answers`

This keeps transactional metadata in PostgreSQL while allowing semantic search to evolve independently.
