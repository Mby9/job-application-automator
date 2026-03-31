"""
Company discovery via DuckDuckGo site-restricted searches.
Finds companies using each ATS platform by searching their known domains,
then extracts board tokens directly from the result URLs.
No manual token entry required.
"""
import re
import asyncio
from typing import List, Dict
from ddgs import DDGS
from core.logger_config import get_logger

logger = get_logger(__name__)

ATS_CONFIGS = {
    "greenhouse": {
        "search_domain": "boards.greenhouse.io",
        "url_regex": r"boards\.greenhouse\.io/([^/?#\s]+)",
    },
    "lever": {
        "search_domain": "jobs.lever.co",
        "url_regex": r"jobs\.lever\.co/([^/?#\s]+)",
    },
    "ashby": {
        "search_domain": "jobs.ashbyhq.com",
        "url_regex": r"jobs\.ashbyhq\.com/([^/?#\s]+)",
    },
    "workable": {
        "search_domain": "apply.workable.com",
        "url_regex": r"apply\.workable\.com/([^/?#\s]+)",
    },
    "rippling": {
        "search_domain": "rippling-ats.com",
        "url_regex": r"([^/?#\s]+)\.rippling-ats\.com",
    },
    "bamboohr": {
        "search_domain": "bamboohr.com/careers",
        "url_regex": r"([^/?#\s]+)\.bamboohr\.com",
    },
}

# Tokens to skip — these are not company names
BLOCKLIST = {
    "job", "jobs", "listing", "listings", "embed", "widget",
    "api", "apply", "confirmation", "search", "home", "index",
}


def _token_to_name(token: str) -> str:
    """Converts a board token like 'shopify' or 'open-ai' to a display name."""
    return token.replace("-", " ").replace("_", " ").title()


def _extract_token(url: str, regex: str) -> str | None:
    """Extracts the board token from a URL using the provided regex."""
    match = re.search(regex, url, re.IGNORECASE)
    if not match:
        return None
    token = match.group(1).split("/")[0].lower().strip()
    if not token or token in BLOCKLIST or len(token) < 2:
        return None
    return token


def _build_queries(ats_domain: str, keywords: List[str], locations: List[str]) -> List[str]:
    """Builds a list of DuckDuckGo queries for a given ATS domain."""
    queries = []
    keyword_str = " ".join(k for k in keywords[:2]) if keywords else ""
    location_str = " ".join(l for l in locations[:2]) if locations else ""
    base = f"site:{ats_domain}"
    
    if keyword_str and location_str:
        queries.append(f"{base} {keyword_str} {location_str}")
    if keyword_str:
        queries.append(f"{base} {keyword_str}")
    if location_str:
        queries.append(f"{base} {location_str}")
    if not queries:
        queries.append(base)
    return queries


def discover_companies(
    keywords: List[str],
    locations: List[str],
    max_results_per_query: int = 20,
) -> List[Dict]:
    """
    Runs DuckDuckGo searches for each ATS platform and extracts company tokens from result URLs.
    Returns a list of dicts: {name, ats_type, board_token, source_url}
    """
    discovered: Dict[str, Dict] = {}  # board_token -> company dict (dedup key)

    with DDGS(timeout=10) as ddgs:
        for ats_type, config in ATS_CONFIGS.items():
            queries = _build_queries(config["search_domain"], keywords, locations)
            for query in queries:
                try:
                    results = list(ddgs.text(query, max_results=max_results_per_query))
                    for result in results:
                        url = result.get("href") or result.get("url", "")
                        token = _extract_token(url, config["url_regex"])
                        if not token:
                            continue
                        unique_key = f"{ats_type}:{token}"
                        if unique_key not in discovered:
                            discovered[unique_key] = {
                                "name": _token_to_name(token),
                                "ats_type": ats_type,
                                "board_token": token,
                                "source_url": url,
                            }
                except Exception as e:
                    logger.warning("Discovery query failed '%s': %s", query, e)
                    continue

    logger.info("Discovery complete — %d unique companies found", len(discovered))
    return list(discovered.values())
