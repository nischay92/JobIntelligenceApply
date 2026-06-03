# API Design

The public API is REST over JSON. All routes are versioned under `/api/v1`.

## API Principles

- Authentication is required unless noted.
- IDs are UUIDs.
- All application content generation produces drafts.
- No endpoint submits job applications.
- Apply URLs are exposed for user review and manual action only.
- API responses use typed schemas and explicit status fields.

## Authentication

### `GET /api/v1/auth/google/login`

Starts Google OAuth.

Auth: public

Response:

```json
{
  "authorization_url": "https://accounts.google.com/..."
}
```

### `GET /api/v1/auth/google/callback`

Handles OAuth callback and creates or updates the user profile.

Auth: public

### `POST /api/v1/auth/logout`

Ends the current session.

Auth: required

### `GET /api/v1/auth/me`

Returns the authenticated user profile.

Auth: required

## Resumes

### `POST /api/v1/resumes`

Uploads a PDF or DOCX resume.

Auth: required

Request: multipart form data

Response:

```json
{
  "id": "uuid",
  "original_filename": "resume.pdf",
  "status": "uploaded"
}
```

### `GET /api/v1/resumes`

Lists user resumes.

Auth: required

### `GET /api/v1/resumes/{resume_id}`

Returns resume metadata and parsed profile.

Auth: required

### `POST /api/v1/resumes/{resume_id}/parse`

Queues or triggers parsing.

Auth: required

Response:

```json
{
  "resume_id": "uuid",
  "status": "parsing"
}
```

### `PATCH /api/v1/resumes/{resume_id}/active`

Marks a resume as the default scoring resume.

Auth: required

## Jobs

### `GET /api/v1/jobs`

Searches and filters discovered jobs.

Auth: required

Query parameters:

- `q`
- `company`
- `location`
- `remote_policy`
- `priority`
- `min_score`
- `source`
- `page`
- `page_size`

### `GET /api/v1/jobs/{job_id}`

Returns job details, parsed description, and current user's match if available.

Auth: required

### `POST /api/v1/jobs/discovery-runs`

Creates a user-visible discovery request. This does not bypass scheduler rules or source limits.

Auth: required

Response:

```json
{
  "run_id": "uuid",
  "status": "queued"
}
```

## Matches

### `GET /api/v1/matches`

Lists scored job matches for the current user.

Auth: required

Query parameters:

- `resume_id`
- `priority`
- `min_score`
- `sort`
- `page`
- `page_size`

### `POST /api/v1/matches/score`

Scores one or more jobs against a resume.

Auth: required

Request:

```json
{
  "resume_id": "uuid",
  "job_ids": ["uuid"]
}
```

Response:

```json
{
  "status": "queued",
  "job_count": 1
}
```

### `GET /api/v1/matches/{match_id}`

Returns detailed scoring output.

Auth: required

Response shape:

```json
{
  "overall": 88,
  "skills": 91,
  "experience": 85,
  "education": 90,
  "missing_skills": ["Kafka", "Terraform"],
  "missing_keywords": ["event streaming"],
  "reasons": ["Strong backend experience", "Relevant cloud experience"],
  "priority": "high",
  "priority_reason": "Strong match with minor infrastructure keyword gaps."
}
```

## Generated Answers

### `POST /api/v1/generated-answers`

Generates draft application content. This endpoint never sends or submits content externally.

Auth: required

Request:

```json
{
  "resume_id": "uuid",
  "job_id": "uuid",
  "content_type": "cover_letter",
  "prompt_label": "Why do you want to work here?"
}
```

Response:

```json
{
  "id": "uuid",
  "status": "draft",
  "content": "Generated draft content..."
}
```

### `GET /api/v1/generated-answers`

Lists generated drafts.

Auth: required

### `PATCH /api/v1/generated-answers/{answer_id}`

Updates status or user-edited content.

Auth: required

Allowed statuses:

- `draft`
- `approved`
- `archived`

Approval records the user's review state only. It does not trigger external submission.

## Saved Jobs

### `POST /api/v1/saved-jobs`

Saves a job for tracking.

Auth: required

### `GET /api/v1/saved-jobs`

Lists saved jobs.

Auth: required

### `PATCH /api/v1/saved-jobs/{saved_job_id}`

Updates notes or application status.

Auth: required

### `DELETE /api/v1/saved-jobs/{saved_job_id}`

Removes a saved job.

Auth: required

## Search Preferences

### `GET /api/v1/preferences/search`

Returns job search and ranking preferences.

Auth: required

### `PUT /api/v1/preferences/search`

Updates job search and ranking preferences.

Auth: required

## Notifications

### `GET /api/v1/notifications`

Lists notification history.

Auth: required

### `PUT /api/v1/notifications/preferences`

Updates channel preferences.

Auth: required

### `POST /api/v1/notifications/test`

Sends a user-approved test notification through a configured channel.

Auth: required

## Internal Service APIs

Internal APIs are network-restricted and authenticated with service credentials.

### AI Service

- `POST /internal/v1/resumes/parse`
- `POST /internal/v1/jobs/parse`
- `POST /internal/v1/matches/score`
- `POST /internal/v1/generation/application-content`
- `POST /internal/v1/embeddings`

### Scheduler Service

- `POST /internal/v1/discovery/run`
- `POST /internal/v1/digests/hourly`
- `POST /internal/v1/digests/daily`
- `POST /internal/v1/summaries/weekly`
- `POST /internal/v1/retries/run`

## Error Shape

```json
{
  "error": {
    "code": "validation_error",
    "message": "File type is not supported.",
    "details": {
      "allowed_types": ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    }
  }
}
```

## Rate-Limited Operations

- OAuth login and callback.
- Resume upload.
- Resume parsing.
- Job scoring.
- Application content generation.
- Manual discovery requests.
- Notification tests.
