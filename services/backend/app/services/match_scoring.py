import re

from app.db.models import Job, Resume

SCORING_MODEL = "deterministic-keyword-v1"
TECH_TERMS = {
    "python",
    "fastapi",
    "django",
    "flask",
    "react",
    "typescript",
    "javascript",
    "postgresql",
    "postgres",
    "mysql",
    "redis",
    "aws",
    "gcp",
    "azure",
    "docker",
    "kubernetes",
    "terraform",
    "kafka",
    "graphql",
    "rest",
    "sql",
    "node",
    "java",
    "go",
    "rust",
}


def score_resume_against_job(*, resume: Resume, job: Job) -> dict:
    profile = resume.parsed_profile or {}
    resume_skills = _normalize_terms(profile.get("skills", []))
    resume_keywords = _normalize_terms(profile.get("keywords", []))
    resume_experience = _normalize_terms(profile.get("experience", []))
    resume_education = _normalize_terms(profile.get("education", []))

    job_text = " ".join(
        [
            job.title,
            job.company,
            job.location or "",
            job.raw_description or "",
            " ".join(job.required_skills or []),
            " ".join(job.preferred_skills or []),
            " ".join(job.technology_stack or []),
        ]
    )
    job_terms = _extract_terms(job_text)
    job_skill_terms = sorted((job_terms & TECH_TERMS) | set(_normalize_terms(job.required_skills or [])))

    matched_skills = sorted(set(resume_skills) & set(job_skill_terms))
    missing_skills = [term for term in job_skill_terms if term not in resume_skills][:10]
    skill_score = _coverage_score(matched_skills, job_skill_terms, default=70)

    matched_keywords = sorted(set(resume_keywords) & job_terms)
    missing_keywords = [term for term in sorted(job_terms) if term not in resume_keywords][:10]
    keyword_score = _coverage_score(matched_keywords, sorted(job_terms), default=65)

    experience_score = _experience_score(resume_experience, job_terms)
    education_score = 90 if resume_education else 70
    overall = round((skill_score * 0.45) + (experience_score * 0.30) + (education_score * 0.15) + (keyword_score * 0.10))
    priority, priority_reason = _priority(overall, missing_skills)

    reasons = _reasons(
        matched_skills=matched_skills,
        resume_experience=resume_experience,
        remote_policy=job.remote_policy,
        overall=overall,
    )

    return {
        "overall_score": overall,
        "skill_score": skill_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "missing_skills": missing_skills,
        "missing_keywords": missing_keywords,
        "match_reasons": reasons,
        "priority": priority,
        "priority_reason": priority_reason,
        "scoring_model": SCORING_MODEL,
    }


def _normalize_terms(values: list[str]) -> list[str]:
    terms = []
    for value in values:
        terms.extend(_extract_terms(value))
    return sorted(set(terms))


def _extract_terms(value: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{1,}", value)}


def _coverage_score(matches: list[str], required: list[str], *, default: int) -> int:
    if not required:
        return default
    return min(100, round((len(matches) / len(required)) * 100))


def _experience_score(resume_experience: list[str], job_terms: set[str]) -> int:
    if not resume_experience:
        return 55
    overlap = len(set(resume_experience) & job_terms)
    return min(95, 70 + overlap * 5)


def _priority(overall: int, missing_skills: list[str]) -> tuple[str, str]:
    if overall >= 80:
        return "high", "Strong match with manageable gaps."
    if overall >= 60:
        return "medium", "Promising match but missing skills should be reviewed."
    return "low", "Lower match based on current resume and job keywords."


def _reasons(
    *,
    matched_skills: list[str],
    resume_experience: list[str],
    remote_policy: str,
    overall: int,
) -> list[str]:
    reasons = []
    if matched_skills:
        reasons.append(f"Matched skills: {', '.join(matched_skills[:6])}.")
    if resume_experience:
        reasons.append("Parsed resume includes relevant experience entries.")
    if remote_policy == "remote":
        reasons.append("Role is marked remote.")
    reasons.append(f"Overall deterministic match score is {overall}.")
    return reasons
