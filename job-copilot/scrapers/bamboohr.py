"""
BambooHR ATS scraper.
Endpoint: GET https://{token}.bamboohr.com/careers/list
"""
import httpx
from typing import List, Dict, Any
from core.logger_config import get_logger

logger = get_logger(__name__)

async def scrape_bamboohr(board_token: str, company_name: str) -> List[Dict[str, Any]]:
    """
    Fetches all jobs from a BambooHR careers list.
    """
    url = f"https://{board_token}.bamboohr.com/careers/list"
    logger.debug("GET %s", url)
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        logger.error("BambooHR scrape failed [%s / %s]: %s", company_name, board_token, e)
        return []

    jobs = data.get("result", [])
    normalized = []

    for job in jobs:
        loc = job.get("location", {})
        location_parts = [loc.get("city"), loc.get("state"), loc.get("country")]
        location_str = ", ".join(filter(None, location_parts))
        
        normalized.append({
            "title": job.get("jobOpeningName", ""),
            "company": company_name,
            "location": location_str,
            "url": f"https://{board_token}.bamboohr.com/careers/{job.get('id')}",
            "description": "",  # Bamboo list API doesn't include full description
            "ats_source": "bamboohr",
            "posted_at": "", # Bamboo list API doesn't easily expose date
            "salary_range": "",
        })

    logger.info("BambooHR [%s] → %d jobs", company_name, len(normalized))
    return normalized
