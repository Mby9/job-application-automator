"""
Greenhouse ATS scraper.
Uses the public Job Board API — no authentication required.
Endpoint: GET https://api.greenhouse.io/v1/boards/{token}/jobs?content=true
"""
import httpx
from typing import List, Dict, Any
from core.logger_config import get_logger

logger = get_logger(__name__)
GREENHOUSE_BASE = "https://api.greenhouse.io/v1/boards"


async def scrape_greenhouse(board_token: str, company_name: str) -> List[Dict[str, Any]]:
    """
    Fetches all jobs from a Greenhouse board.
    Returns a normalized list of RawJob dicts.
    """
    url = f"{GREENHOUSE_BASE}/{board_token}/jobs?content=true"
    logger.debug("GET %s", url)
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            logger.debug("Response %d from %s", response.status_code, url)
            data = response.json()
    except Exception as e:
        logger.error("Greenhouse scrape failed [%s / %s]: %s", company_name, board_token, e)
        return []

    jobs = data.get("jobs", [])
    normalized = []

    for job in jobs:
        # Location: prefer office name, fall back to location object
        location = ""
        offices = job.get("offices") or []
        if offices:
            location = offices[0].get("name", "")
        if not location:
            loc_obj = job.get("location") or {}
            location = loc_obj.get("name", "")

        # Description: strip basic HTML tags
        description = _strip_html(job.get("content") or job.get("absolute_url", ""))

        normalized.append({
            "title": job.get("title", ""),
            "company": company_name,
            "location": location,
            "url": job.get("absolute_url", ""),
            "description": description[:1000],  # Cap for DB storage
            "ats_source": "greenhouse",
            "posted_at": job.get("updated_at", ""),
            "salary_range": "",
        })

    logger.info("Greenhouse [%s] → %d jobs", company_name, len(normalized))
    return normalized


def _strip_html(text: str) -> str:
    """Very lightweight HTML tag stripper."""
    import re
    return re.sub(r"<[^>]+>", " ", text).strip()
