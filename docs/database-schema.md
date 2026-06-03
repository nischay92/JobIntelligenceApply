# Database Schema

PostgreSQL is the source of truth for relational data. ChromaDB stores embeddings with metadata references back to PostgreSQL records.

## Conventions

- Primary keys use UUIDs.
- Timestamps use `created_at` and `updated_at`.
- Tenant-owned tables include `user_id`.
- Soft-delete can be added later with `deleted_at` where needed.
- External source identifiers are indexed to prevent duplicate jobs.

## Tables

### users

Stores authenticated user profiles from Google OAuth.

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| google_sub | text | Unique Google subject |
| email | text | Unique, indexed |
| name | text | Display name |
| avatar_url | text | Optional |
| timezone | text | Defaults to user locale or UTC |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

Indexes:

- Unique `google_sub`
- Unique `email`

### resumes

Stores uploaded resume metadata, parsed profile JSON, and vector references.

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| user_id | uuid | Foreign key to `users.id` |
| original_filename | text | Required |
| file_mime_type | text | PDF or DOCX |
| file_size_bytes | bigint | Required |
| storage_path | text | Required |
| status | text | uploaded, parsing, parsed, failed |
| parsed_profile | jsonb | Structured resume JSON |
| active | boolean | Current default resume |
| vector_collection | text | Chroma collection name |
| vector_id | text | Chroma vector id |
| parse_error | text | Optional |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

Indexes:

- `(user_id, active)`
- `(user_id, status)`
- GIN index on `parsed_profile`

### jobs

Stores normalized public job listings.

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| source | text | greenhouse, lever, ashby, wellfound, yc_jobs, rss, company_page |
| external_id | text | Source-specific id when available |
| company | text | Required |
| title | text | Required |
| location | text | Optional |
| employment_type | text | Optional |
| salary_min | integer | Optional |
| salary_max | integer | Optional |
| salary_currency | text | Optional |
| description_url | text | Direct public link |
| apply_url | text | Direct public application link, shown only for user action |
| raw_description | text | Original job description |
| parsed_description | jsonb | Structured job JSON |
| required_skills | text[] | Extracted required skills |
| preferred_skills | text[] | Extracted preferred skills |
| technology_stack | text[] | Extracted technologies |
| years_experience_min | numeric | Optional |
| years_experience_max | numeric | Optional |
| sponsorship_hints | text[] | Optional |
| security_clearance_required | boolean | Defaults false |
| remote_policy | text | remote, hybrid, onsite, unknown |
| status | text | discovered, parsed, scored, expired, failed |
| vector_collection | text | Chroma collection name |
| vector_id | text | Chroma vector id |
| discovered_at | timestamptz | Required |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

Indexes:

- Unique `(source, external_id)` where `external_id` is not null
- Unique `description_url`
- `(company, title)`
- `(status, discovered_at)`
- GIN indexes on `required_skills`, `preferred_skills`, `technology_stack`, and `parsed_description`

### job_matches

Stores scored resume-to-job matches.

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| user_id | uuid | Foreign key to `users.id` |
| resume_id | uuid | Foreign key to `resumes.id` |
| job_id | uuid | Foreign key to `jobs.id` |
| overall_score | integer | 0-100 |
| skill_score | integer | 0-100 |
| experience_score | integer | 0-100 |
| education_score | integer | 0-100 |
| missing_skills | text[] | Optional |
| missing_keywords | text[] | Optional |
| match_reasons | text[] | Optional |
| priority | text | high, medium, low |
| priority_reason | text | Explanation |
| scoring_model | text | AI/scoring version |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

Indexes:

- Unique `(user_id, resume_id, job_id)`
- `(user_id, priority, overall_score desc)`
- `(user_id, created_at desc)`

### generated_answers

Stores generated application support content as drafts only.

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| user_id | uuid | Foreign key to `users.id` |
| resume_id | uuid | Foreign key to `resumes.id` |
| job_id | uuid | Foreign key to `jobs.id` |
| content_type | text | cover_letter, resume_suggestions, recruiter_email, linkedin_message, question_answer |
| prompt_label | text | Optional application question |
| content | text | Generated draft |
| metadata | jsonb | Optional |
| status | text | draft, approved, archived |
| vector_collection | text | Chroma collection name |
| vector_id | text | Chroma vector id |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

Indexes:

- `(user_id, job_id, content_type)`
- `(user_id, status)`

### notifications

Stores outbound notification attempts and delivery state.

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| user_id | uuid | Foreign key to `users.id` |
| channel | text | email, telegram, discord |
| notification_type | text | hourly_digest, daily_digest, weekly_summary |
| subject | text | Optional |
| body | text | Rendered notification body |
| status | text | pending, sent, failed, skipped |
| provider_message_id | text | Optional |
| error | text | Optional |
| sent_at | timestamptz | Optional |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

Indexes:

- `(user_id, notification_type, created_at desc)`
- `(status, created_at)`

### saved_jobs

Stores user-saved opportunities.

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| user_id | uuid | Foreign key to `users.id` |
| job_id | uuid | Foreign key to `jobs.id` |
| notes | text | Optional |
| application_status | text | interested, applied, interviewing, offer, rejected, archived |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

Indexes:

- Unique `(user_id, job_id)`
- `(user_id, application_status)`

### search_preferences

Stores user search and ranking preferences.

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| user_id | uuid | Foreign key to `users.id` |
| target_titles | text[] | Optional |
| target_locations | text[] | Optional |
| remote_preference | text | remote, hybrid, onsite, flexible |
| min_salary | integer | Optional |
| visa_sponsorship_required | boolean | Defaults false |
| preferred_technologies | text[] | Optional |
| excluded_companies | text[] | Optional |
| notification_channels | text[] | email, telegram, discord |
| hourly_digest_enabled | boolean | Defaults true |
| daily_digest_enabled | boolean | Defaults false |
| weekly_summary_enabled | boolean | Defaults false |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

Indexes:

- Unique `user_id`

### processing_runs

Tracks scheduler and background workflow history.

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| run_type | text | discovery, parsing, scoring, digest, retry, summary |
| status | text | running, succeeded, failed, partial |
| source | text | Optional discovery source |
| started_at | timestamptz | Required |
| finished_at | timestamptz | Optional |
| records_seen | integer | Defaults 0 |
| records_created | integer | Defaults 0 |
| records_updated | integer | Defaults 0 |
| error | text | Optional |
| metadata | jsonb | Optional |

Indexes:

- `(run_type, started_at desc)`
- `(status, started_at)`

## ChromaDB Collections

### resume_embeddings

Metadata:

- `user_id`
- `resume_id`
- `section`
- `source_type = resume`

### job_embeddings

Metadata:

- `job_id`
- `company`
- `title`
- `source`
- `source_type = job`

### generated_content_embeddings

Metadata:

- `user_id`
- `job_id`
- `generated_answer_id`
- `content_type`
- `source_type = generated_answer`
