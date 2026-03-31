"""
Rippling ATS scraper.
Endpoint: GET https://{token}.rippling-ats.com/api/v1/board
"""
import httpx
from typing import List, Dict, Any
from core.logger_config import get_logger
import re

logger = get_logger(__name__)

async def scrape_rippling(board_token: str, company_name: str) -> List[Dict[str, Any]]:
    """
    Fetches all jobs from a Rippling board.
    """
    url = f"https://{board_token}.rippling-ats.com/api/v1/board"
    logger.debug("GET %s", url)
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        logger.error("Rippling scrape failed [%s / %s]: %s", company_name, board_token, e)
        return []

    jobs = data.get("jobs", [])
    normalized = []

    for job in jobs:
        loc = job.get("workLocation", {})
        location_str = loc.get("name", "")
        
        desc = re.sub(r"<[^>]+>", " ", job.get("description", "")).strip()
        
        # Determine salary range if compensation object exists
        salary_range = ""
        comp = job.get("compensation")
        if comp:
            min_sal = comp.get("minRange")
            max_sal = comp.get("maxRange")
            if min_sal and max_sal:
                salary_range = f"${min_sal} - ${max_sal}"

        normalized.append({
            "title": job.get("name", ""),
            "company": company_name,
            "location": location_str,
            "url": job.get("url", ""),
            "description": desc[:1000],
            "ats_source": "rippling",
            "posted_at": job.get("createdAt", ""),
            "salary_range": salary_range,
        })

    logger.info("Rippling [%s] → %d jobs", company_name, len(normalized))
    return normalized
