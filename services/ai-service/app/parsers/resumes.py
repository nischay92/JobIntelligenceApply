from collections import Counter
from io import BytesIO
import re
from zipfile import BadZipFile

from docx import Document
from fastapi import HTTPException, UploadFile, status
from pypdf import PdfReader

from app.schemas.resumes import ParsedResumeProfile

PDF_MIME = "application/pdf"
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

SECTION_ALIASES = {
    "skills": {"skills", "technical skills", "technologies", "core skills"},
    "experience": {"experience", "work experience", "professional experience", "employment"},
    "projects": {"projects", "selected projects", "personal projects"},
    "education": {"education", "academic background"},
    "certifications": {"certifications", "certificates", "licenses"},
}

COMMON_STOPWORDS = {
    "and",
    "for",
    "with",
    "the",
    "that",
    "this",
    "from",
    "into",
    "using",
    "will",
    "your",
    "you",
    "are",
    "was",
    "were",
    "have",
    "has",
    "had",
    "resume",
}


async def extract_resume_text(upload: UploadFile) -> str:
    data = await upload.read()
    await upload.close()

    if upload.content_type == PDF_MIME:
        return _extract_pdf_text(data)
    if upload.content_type == DOCX_MIME:
        return _extract_docx_text(data)

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail="Resume must be a PDF or DOCX file.",
    )


def parse_resume_text(text: str) -> ParsedResumeProfile:
    normalized = _normalize_text(text)
    sections = _split_sections(normalized)
    skills = _parse_skills(sections.get("skills", []))

    return ParsedResumeProfile(
        skills=skills,
        experience=_parse_bullets(sections.get("experience", [])),
        projects=_parse_bullets(sections.get("projects", [])),
        education=_parse_bullets(sections.get("education", [])),
        certifications=_parse_bullets(sections.get("certifications", [])),
        keywords=_extract_keywords(normalized, skills),
    )


def _extract_pdf_text(data: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unable to read PDF resume.",
        ) from exc


def _extract_docx_text(data: bytes) -> str:
    try:
        document = Document(BytesIO(data))
    except BadZipFile as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unable to read DOCX resume.",
        ) from exc

    paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
    return "\n".join(paragraphs).strip()


def _normalize_text(text: str) -> str:
    return "\n".join(line.strip() for line in text.replace("\x00", "").splitlines() if line.strip())


def _split_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current_section = "experience"

    for line in text.splitlines():
        section_name = _section_name(line)
        if section_name:
            current_section = section_name
            sections.setdefault(current_section, [])
            continue
        sections.setdefault(current_section, []).append(line)

    return sections


def _section_name(line: str) -> str | None:
    compact = re.sub(r"[^a-z ]", "", line.lower()).strip()
    for section, aliases in SECTION_ALIASES.items():
        if compact in aliases:
            return section
    return None


def _parse_skills(lines: list[str]) -> list[str]:
    raw_items: list[str] = []
    for line in lines:
        raw_items.extend(re.split(r"[,|;/•]", line))

    skills = []
    for item in raw_items:
        skill = re.sub(r"\s+", " ", item.strip(" -\t")).strip()
        if 1 < len(skill) <= 40 and not skill.lower().startswith(("experience", "projects")):
            skills.append(skill)
    return _dedupe(skills)


def _parse_bullets(lines: list[str]) -> list[str]:
    items = []
    for line in lines:
        item = re.sub(r"^[\-*•]\s*", "", line).strip()
        if len(item) > 3:
            items.append(item)
    return items[:12]


def _extract_keywords(text: str, skills: list[str]) -> list[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{2,}", text)
    counts = Counter(token for token in tokens if token.lower() not in COMMON_STOPWORDS)
    candidates = [word for word, _count in counts.most_common(40)]
    return _dedupe(skills + candidates)[:40]


def _dedupe(items: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for item in items:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped
