from uuid import uuid4

from app.db.models import Job, JobMatch, Resume

DRAFT_DISCLAIMER = "Draft for human review. ApplyWise AI does not submit applications or send messages."


def generate_application_content(
    *,
    resume: Resume,
    job: Job,
    match: JobMatch | None,
    content_type: str,
    prompt_label: str | None,
) -> dict:
    profile = resume.parsed_profile or {}
    skills = _join(profile.get("skills", []), fallback="your relevant technical skills")
    experience = _join(profile.get("experience", []), fallback="your software engineering experience")
    missing_skills = _join(match.missing_skills if match else [], fallback="No major gaps identified")
    reasons = _join(match.match_reasons if match else [], fallback="The role aligns with your parsed resume.")
    score = match.overall_score if match else "not yet scored"

    templates = {
        "resume_suggestions": _resume_suggestions(job, skills, missing_skills),
        "missing_keywords": _missing_keywords(match),
        "cover_letter": _cover_letter(job, skills, experience, reasons),
        "recruiter_email": _recruiter_email(job, skills, score),
        "linkedin_message": _linkedin_message(job, skills),
        "why_company": _why_company(job, skills),
        "tell_me_about_yourself": _tell_me_about_yourself(skills, experience),
        "why_fit": _why_fit(job, skills, reasons),
        "relevant_experience_summary": _experience_summary(job, experience),
    }
    content = templates[content_type]
    if prompt_label and content_type not in templates:
        content = f"{prompt_label}\n\n{content}"

    return {
        "content": f"{content}\n\n{DRAFT_DISCLAIMER}",
        "metadata": {
            "generator": "deterministic-template-v1",
            "match_score": score,
            "missing_skills": match.missing_skills if match else [],
            "human_approval_required": True,
        },
        "vector_id": f"generated-{uuid4()}",
    }


def _resume_suggestions(job: Job, skills: str, missing_skills: str) -> str:
    return (
        f"Tailored resume suggestions for {job.title} at {job.company}:\n"
        f"- Emphasize experience connected to {skills}.\n"
        f"- Mirror relevant terms from the job description where truthful.\n"
        f"- Address gaps to review: {missing_skills}.\n"
        "- Keep the original resume unchanged; save edits as a separate tailored copy."
    )


def _missing_keywords(match: JobMatch | None) -> str:
    if not match or not match.missing_keywords:
        return "Missing keywords to review: no major keyword gaps were detected."
    return "Missing keywords to review:\n" + "\n".join(f"- {keyword}" for keyword in match.missing_keywords[:12])


def _cover_letter(job: Job, skills: str, experience: str, reasons: str) -> str:
    return (
        f"Dear {job.company} Hiring Team,\n\n"
        f"I am excited to apply for the {job.title} role. My background includes {experience}, "
        f"with hands-on strengths in {skills}.\n\n"
        f"What stands out about this opportunity is the alignment between the role and my experience. "
        f"{reasons}\n\n"
        "I would welcome the chance to discuss how I can contribute to your engineering team.\n\n"
        "Best,\n[Your Name]"
    )


def _recruiter_email(job: Job, skills: str, score: int | str) -> str:
    return (
        f"Subject: Interest in {job.title} at {job.company}\n\n"
        f"Hi [Recruiter Name],\n\n"
        f"I came across the {job.title} opening at {job.company} and wanted to reach out. "
        f"My background includes {skills}, and ApplyWise scored this as a {score} match against my parsed resume.\n\n"
        "I would appreciate the opportunity to learn more about the role and share how my experience maps to the team’s needs.\n\n"
        "Best,\n[Your Name]"
    )


def _linkedin_message(job: Job, skills: str) -> str:
    return (
        f"Hi [Name], I saw the {job.title} role at {job.company} and noticed a strong fit with my background in {skills}. "
        "I would be grateful for any guidance on the role or the best way to connect with the hiring team."
    )


def _why_company(job: Job, skills: str) -> str:
    return (
        f"I am interested in {job.company} because the {job.title} role appears to connect directly with my strengths in {skills}. "
        "I am especially motivated by opportunities where I can contribute to practical engineering outcomes and keep growing with a strong team."
    )


def _tell_me_about_yourself(skills: str, experience: str) -> str:
    return (
        f"I am a software engineer with experience in {experience}. My technical strengths include {skills}. "
        "I enjoy building reliable systems, learning quickly, and translating product goals into maintainable engineering work."
    )


def _why_fit(job: Job, skills: str, reasons: str) -> str:
    return (
        f"I am a strong fit for the {job.title} role because my background includes {skills}. "
        f"The match analysis highlighted: {reasons}"
    )


def _experience_summary(job: Job, experience: str) -> str:
    return (
        f"Relevant experience summary for {job.title} at {job.company}:\n"
        f"{experience}\n\n"
        "Use this as a concise starting point and verify every claim before submitting."
    )


def _join(values: list[str], *, fallback: str) -> str:
    cleaned = [value.strip() for value in values if value and value.strip()]
    return ", ".join(cleaned[:8]) if cleaned else fallback
