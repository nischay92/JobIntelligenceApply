from datetime import UTC, datetime
import re
from typing import Protocol

import httpx


class JobConnector(Protocol):
    async def discover(self, *, board_token: str | None, company: str | None, limit: int) -> list[dict]:
        pass


class GreenhouseConnector:
    async def discover(self, *, board_token: str | None, company: str | None, limit: int) -> list[dict]:
        token = _require_board_token(board_token, "Greenhouse")
        url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url)
        response.raise_for_status()
        jobs = response.json().get("jobs", [])
        normalized = []
        for job in jobs[:limit]:
            normalized.append(
                {
                    "source": "greenhouse",
                    "external_id": str(job["id"]),
                    "company": company or token,
                    "title": job.get("title") or "Untitled role",
                    "location": (job.get("location") or {}).get("name"),
                    "employment_type": None,
                    "description_url": job.get("absolute_url") or url,
                    "apply_url": job.get("absolute_url"),
                    "raw_description": _strip_html(job.get("content") or ""),
                    "remote_policy": _remote_policy(job.get("title", ""), (job.get("location") or {}).get("name")),
                    "status": "discovered",
                    "security_clearance_required": _mentions_clearance(job.get("content") or ""),
                    "discovered_at": datetime.now(UTC),
                }
            )
        return normalized


class LeverConnector:
    async def discover(self, *, board_token: str | None, company: str | None, limit: int) -> list[dict]:
        token = _require_board_token(board_token, "Lever")
        url = f"https://api.lever.co/v0/postings/{token}?mode=json"
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url)
        response.raise_for_status()
        normalized = []
        for job in response.json()[:limit]:
            categories = job.get("categories") or {}
            location = categories.get("location")
            description = "\n".join(
                [job.get("descriptionPlain") or ""]
                + [item.get("text", "") for item in job.get("lists", []) for item in item.get("content", [])]
            )
            normalized.append(
                {
                    "source": "lever",
                    "external_id": str(job["id"]),
                    "company": company or token,
                    "title": job.get("text") or "Untitled role",
                    "location": location,
                    "employment_type": categories.get("commitment"),
                    "description_url": job.get("hostedUrl") or job.get("applyUrl"),
                    "apply_url": job.get("applyUrl") or job.get("hostedUrl"),
                    "raw_description": description,
                    "remote_policy": _remote_policy(job.get("text", ""), location),
                    "status": "discovered",
                    "security_clearance_required": _mentions_clearance(description),
                    "discovered_at": datetime.now(UTC),
                }
            )
        return normalized


class AshbyConnector:
    async def discover(self, *, board_token: str | None, company: str | None, limit: int) -> list[dict]:
        token = _require_board_token(board_token, "Ashby")
        url = f"https://api.ashbyhq.com/posting-api/job-board/{token}"
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url)
        response.raise_for_status()
        jobs = response.json().get("jobs", [])
        normalized = []
        for job in jobs[:limit]:
            location = (job.get("location") or {}).get("name")
            normalized.append(
                {
                    "source": "ashby",
                    "external_id": str(job["id"]),
                    "company": company or token,
                    "title": job.get("title") or "Untitled role",
                    "location": location,
                    "employment_type": job.get("employmentType"),
                    "description_url": job.get("jobUrl") or url,
                    "apply_url": job.get("applyUrl") or job.get("jobUrl"),
                    "raw_description": _strip_html(job.get("descriptionHtml") or ""),
                    "remote_policy": _remote_policy(job.get("title", ""), location),
                    "status": "discovered",
                    "security_clearance_required": _mentions_clearance(job.get("descriptionHtml") or ""),
                    "discovered_at": datetime.now(UTC),
                }
            )
        return normalized


class SampleConnector:
    async def discover(self, *, board_token: str | None, company: str | None, limit: int) -> list[dict]:
        now = datetime.now(UTC)
        samples = [
            {
                "source": "sample",
                "external_id": "sample-backend-engineer",
                "company": company or "ApplyWise Demo Co",
                "title": "Backend Engineer",
                "location": "Remote",
                "employment_type": "Full-time",
                "description_url": "https://example.com/jobs/backend-engineer",
                "apply_url": "https://example.com/jobs/backend-engineer",
                "raw_description": "Build Python, FastAPI, PostgreSQL services. Human application review required.",
                "remote_policy": "remote",
                "status": "discovered",
                "security_clearance_required": False,
                "discovered_at": now,
            }
        ]
        return samples[:limit]


CONNECTORS: dict[str, JobConnector] = {
    "greenhouse": GreenhouseConnector(),
    "lever": LeverConnector(),
    "ashby": AshbyConnector(),
    "sample": SampleConnector(),
}


def get_connector(source: str) -> JobConnector:
    return CONNECTORS[source]


def _require_board_token(board_token: str | None, source_name: str) -> str:
    if not board_token:
        raise ValueError(f"{source_name} discovery requires a public board token.")
    return board_token.strip()


def _strip_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", text).strip()


def _remote_policy(*values: str | None) -> str:
    combined = " ".join(value or "" for value in values).lower()
    if "remote" in combined:
        return "remote"
    if "hybrid" in combined:
        return "hybrid"
    if "onsite" in combined or "on-site" in combined:
        return "onsite"
    return "unknown"


def _mentions_clearance(value: str) -> bool:
    return "security clearance" in value.lower() or "clearance required" in value.lower()
