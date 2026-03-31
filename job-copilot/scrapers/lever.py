"""
Lever ATS scraper.
Uses the public Postings API — no authentication required.
Endpoint: GET https://api.lever.co/v0/postings/{token}?mode=json
"""
import httpx
import re
from typing import List, Dict, Any
from core.logger_config import get_logger

logger = get_logger(__name__)
LEVER_BASE = "https://api.lever.co/v0/postings"


async def scrape_lever(board_token: str, company_name: str) -> List[Dict[str, Any]]:
    """
    Fetches all postings from a Lever job board.
    Returns a normalized list of RawJob dicts.
    """
    url = f"{LEVER_BASE}/{board_token}?mode=json"
    logger.debug("GET %s", url)
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers={"Accept": "application/json"})
            response.raise_for_status()
            logger.debug("Response %d from %s", response.status_code, url)
            data = response.json()
    except Exception as e:
        logger.error("Lever scrape failed [%s / %s]: %s", company_name, board_token, e)
        return []

    normalized = []
    for job in data:
        categories = job.get("categories") or {}
        location = categories.get("location", "")

        # Build description from lists blocks (responsibilities, requirements, etc.)
        description_parts = []
        for block in job.get("lists", []):
            content = block.get("content", "")
            description_parts.append(_strip_html(content))
        description = " ".join(description_parts) or _strip_html(job.get("additional", ""))

        posted_at = ""
        created_at_ms = job.get("createdAt")
        if created_at_ms:
            import datetime
            try:
                posted_at = datetime.datetime.fromtimestamp(created_at_ms / 1000.0).isoformat()
            except Exception:
                pass

        normalized.append({
            "title": job.get("text", ""),
            "company": company_name,
            "location": location,
            "url": job.get("applyUrl") or job.get("hostedUrl", ""),
            "description": description[:1000],
            "ats_source": "lever",
            "posted_at": posted_at,
            "salary_range": "",
        })

    logger.info("Lever [%s] → %d jobs", company_name, len(normalized))
    return normalized


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text).strip()
