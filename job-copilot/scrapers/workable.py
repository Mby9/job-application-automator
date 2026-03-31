"""
Workable ATS scraper.
Uses the public Widget API.
Endpoint: GET https://apply.workable.com/api/v1/widget/accounts/{token}
"""
import httpx
from typing import List, Dict, Any
from core.logger_config import get_logger

logger = get_logger(__name__)

async def scrape_workable(board_token: str, company_name: str) -> List[Dict[str, Any]]:
    """
    Fetches all jobs from a Workable board.
    """
    url = f"https://apply.workable.com/api/v1/widget/accounts/{board_token}"
    logger.debug("GET %s", url)
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        logger.error("Workable scrape failed [%s / %s]: %s", company_name, board_token, e)
        return []

    jobs = data.get("jobs", [])
    normalized = []

    for job in jobs:
        loc = job.get("location", {})
        location_str = f"{loc.get('city', '')}, {loc.get('country', '')}".strip(", ")
        
        normalized.append({
            "title": job.get("title", ""),
            "company": company_name,
            "location": location_str,
            "url": job.get("url", ""),
            "description": job.get("description", "")[:1000],
            "ats_source": "workable",
            "posted_at": job.get("published_on", ""),
            "salary_range": "",
        })

    logger.info("Workable [%s] → %d jobs", company_name, len(normalized))
    return normalized
