"""
Workday ATS scraper (best-effort).
Workday is a JavaScript SPA with no public API.
This scraper uses Playwright to render the page and extract visible job listings.
Fails gracefully — returns [] if blocked or timed out.
"""
import re
from typing import List, Dict, Any
from core.logger_config import get_logger

logger = get_logger(__name__)


async def scrape_workday(career_url: str, company_name: str) -> List[Dict[str, Any]]:
    """
    Scrapes a Workday career page using Playwright.
    
    Args:
        career_url: The full URL of the company's Workday career page
                    e.g. https://company.wd1.myworkdayjobs.com/careers
        company_name: Display name for the company

    Returns:
        Normalized list of RawJob dicts, or [] on failure.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.warning("Playwright not installed — skipping Workday scrape for '%s'", company_name)
        return []

    jobs = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_extra_http_headers({
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                )
            })
            await page.goto(career_url, timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)  # Allow JS to render job list

            # Workday renders jobs inside list items with data-automation-id
            job_elements = await page.query_selector_all(
                "[data-automation-id='jobTitle'], li[class*='job'] a, a[data-automation-id*='job']"
            )

            for el in job_elements[:50]:  # Cap at 50 per company
                title = (await el.inner_text()).strip()
                url = await el.get_attribute("href") or career_url
                if url.startswith("/"):
                    # Make relative URLs absolute
                    from urllib.parse import urlparse
                    parsed = urlparse(career_url)
                    url = f"{parsed.scheme}://{parsed.netloc}{url}"

                if title:
                    jobs.append({
                        "title": title,
                        "company": company_name,
                        "location": "",  # Workday location is often on detail page
                        "url": url,
                        "description": "",
                        "ats_source": "workday",
                        "posted_at": "",
                        "salary_range": "",
                    })

            await browser.close()
    except Exception as e:
        logger.error("Workday scrape failed [%s]: %s", company_name, e)
        return []

    logger.info("Workday [%s] → %d jobs", company_name, len(jobs))
    return jobs
