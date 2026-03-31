"""
Ashby ATS scraper.
Uses the public posting API — no authentication required.
Endpoint: GET https://api.ashbyhq.com/posting-api/job-board/{token}
"""
import httpx
import re
from typing import List, Dict, Any
from core.logger_config import get_logger

logger = get_logger(__name__)
ASHBY_BASE = "https://api.ashbyhq.com/posting-api/job-board"


async def scrape_ashby(board_token: str, company_name: str) -> List[Dict[str, Any]]:
    """
    Fetches all jobs from an Ashby job board.
    Returns a normalized list of RawJob dicts.
    """
    url = f"{ASHBY_BASE}/{board_token}"
    logger.debug("GET %s", url)
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            logger.debug("Response %d from %s", response.status_code, url)
            data = response.json()
    except Exception as e:
        logger.error("Ashby scrape failed [%s / %s]: %s", company_name, board_token, e)
        return []

    jobs = data.get("jobs", [])
    normalized = []

    for job in jobs:
        # Location: try multiple fields Ashby uses
        location = (
            job.get("location")
            or job.get("locationName")
            or job.get("primaryLocation", {}).get("name", "")
            or ""
        )

        # Description from descriptionHtml or description
        description = _strip_html(
            job.get("descriptionHtml") or job.get("description") or ""
        )

        # Job URL: build from jobUrl or construct from token
        job_url = (
            job.get("jobUrl")
            or job.get("applyUrl")
            or f"https://jobs.ashbyhq.com/{board_token}/{job.get('id', '')}"
        )

        normalized.append({
            "title": job.get("title", ""),
            "company": company_name,
            "location": location,
            "url": job_url,
            "description": description[:1000],
            "ats_source": "ashby",
            "posted_at": job.get("publishedAt", ""),
            "salary_range": job.get("compensationTierSummary", ""),
        })

    logger.info("Ashby [%s] → %d jobs", company_name, len(normalized))
    return normalized


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text).strip()
