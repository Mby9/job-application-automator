"""
Scraper service orchestration.
Fetches approved companies from DB, dispatches to correct ATS scraper in parallel,
runs the programmatic filter engine, deduplicates, then AI-scores filtered new jobs.
"""
import asyncio
import json
from typing import List, Dict, Any
from core.logger_config import get_logger

logger = get_logger(__name__)

from database_dir.database import SessionLocal, Job, Company, UserPreferences
from services.filter_engine import filter_jobs
from services.ai_engine import analyze_job_fit


async def _scrape_company(company: Company) -> List[Dict[str, Any]]:
    """Dispatches a company to the right scraper based on its ats_type."""
    ats = company.ats_type
    token = company.board_token
    name = company.name

    if ats == "greenhouse":
        from scrapers.greenhouse import scrape_greenhouse
        return await scrape_greenhouse(token, name)
    elif ats == "lever":
        from scrapers.lever import scrape_lever
        return await scrape_lever(token, name)
    elif ats == "ashby":
        from scrapers.ashby import scrape_ashby
        return await scrape_ashby(token, name)
    elif ats == "workday":
        from scrapers.workday import scrape_workday
        # board_token holds the full URL for Workday companies
        return await scrape_workday(token, name)
    elif ats == "workable":
        from scrapers.workable import scrape_workable
        return await scrape_workable(token, name)
    elif ats == "rippling":
        from scrapers.rippling import scrape_rippling
        return await scrape_rippling(token, name)
    elif ats == "bamboohr":
        from scrapers.bamboohr import scrape_bamboohr
        return await scrape_bamboohr(token, name)
    else:
        logger.warning("Unknown ATS type '%s' for company '%s'", ats, name)
        return []


async def discover_and_score_jobs(resume_text: str, user_id: int) -> tuple[List[Job], int]:
    """
    Main pipeline:
    1. Load approved companies + preferences from DB for the specific user
    2. Scrape all companies in parallel
    3. Programmatically filter by location/keywords
    4. Deduplicate against existing DB records (for this user)
    5. Batched AI-score only the new filtered jobs
    6. Persist and return all jobs sorted by match score
    """
    db = SessionLocal()
    from services.state import SCAN_STATUS
    
    def _update_status(msg: str, count: int = 0):
        if user_id in SCAN_STATUS:
            SCAN_STATUS[user_id]["progress"] = msg
            if count > 0:
                SCAN_STATUS[user_id]["discovered_count"] = count
                
    try:
        _update_status("Loading user preferences and approved companies...")
        # --- 1. Load configuration ---
        approved_companies = db.query(Company).filter(
            Company.status == "approved",
            Company.owner_id == user_id
        ).all()
        prefs_row = db.query(UserPreferences).filter(UserPreferences.owner_id == user_id).first()

        preferred_locations: List[str] = []
        preferred_keywords: List[str] = []
        remote_only = False
        seniority_level = "Any"
        legal_work_country = "Any"
        priority_company_names: List[str] = []

        if prefs_row:
            preferred_locations = json.loads(prefs_row.preferred_locations or "[]")
            preferred_keywords = json.loads(prefs_row.preferred_keywords or "[]")
            remote_only = prefs_row.remote_only or False
            seniority_level = prefs_row.seniority_level or "Any"
            legal_work_country = prefs_row.legal_work_country or "Any"

        priority_company_names = [
            c.name for c in approved_companies if c.is_priority
        ]

        if not approved_companies:
            logger.warning("No approved companies found for user %d", user_id)
            all_jobs = db.query(Job).filter(Job.owner_id == user_id).order_by(Job.match_score.desc()).all()
            return all_jobs, 0

        # --- 2. Scrape all companies in parallel ---
        _update_status(f"Scraping active job boards across {len(approved_companies)} companies...")
        logger.info("Scraping %d approved companies in parallel for user %d", len(approved_companies), user_id)
        scrape_tasks = [_scrape_company(c) for c in approved_companies]
        results = await asyncio.gather(*scrape_tasks, return_exceptions=True)

        raw_jobs: List[Dict] = []
        for result in results:
            if isinstance(result, Exception):
                logger.error("Scrape task error: %s", result)
            elif isinstance(result, list):
                raw_jobs.extend(result)

        logger.info("Raw jobs scraped: %d total", len(raw_jobs))

        # --- 3. Programmatic filter ---
        _update_status(f"Applying strict keyword & location filters to {len(raw_jobs)} discovered jobs...")
        filtered_jobs = filter_jobs(
            raw_jobs,
            preferred_locations=preferred_locations,
            preferred_keywords=preferred_keywords,
            remote_only=remote_only,
            priority_companies=priority_company_names,
            seniority_level=seniority_level,
            legal_work_country=legal_work_country,
        )
        logger.info("Jobs after programmatic filter: %d (dropped %d)",
                    len(filtered_jobs), len(raw_jobs) - len(filtered_jobs))

        # --- 4. Deduplicate against DB ---
        existing_db_jobs = db.query(Job.url, Job.title, Job.company).filter(Job.owner_id == user_id).all()
        existing_urls = {row.url for row in existing_db_jobs if row.url}
        existing_title_company = [
            (row.title.lower(), row.company.lower()) 
            for row in existing_db_jobs if row.title and row.company
        ]

        from difflib import SequenceMatcher
        
        new_jobs = []
        for j in filtered_jobs:
            if j.get("url") in existing_urls:
                continue
                
            j_title = j.get("title", "").lower()
            j_company = j.get("company", "").lower()
            
            is_duplicate = False
            for ex_title, ex_company in existing_title_company:
                if ex_company == j_company:
                    # Fuzzy match titles within the same company
                    if SequenceMatcher(None, j_title, ex_title).ratio() > 0.85:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                new_jobs.append(j)
                existing_title_company.append((j_title, j_company))
                
        logger.info("New jobs for user %d: %d", user_id, len(new_jobs))

        # --- 5. Batched AI score new jobs ---
        if new_jobs:
            from services.ai_engine import batch_analyze_job_fit
            import uuid
            
            # Decorate jobs with a temp id string
            for i, job_data in enumerate(new_jobs):
                job_data["_temp_id"] = str(uuid.uuid4())
                
            batch_size = 10
            total_batches = (len(new_jobs) + batch_size - 1) // batch_size
            
            _update_status(f"Scanning {len(new_jobs)} unseen jobs with AI (Batch 1 of {total_batches})...")
            
            for batch_index in range(total_batches):
                _update_status(f"Scanning {len(new_jobs)} unseen jobs with AI (Batch {batch_index + 1} of {total_batches})...")
                start_i = batch_index * batch_size
                batch = new_jobs[start_i:start_i + batch_size]
                
                ai_payload = [
                    {"id": j["_temp_id"], "title": j["title"], "description": j.get("description", "")}
                    for j in batch
                ]
                
                try:
                    scores_map = await batch_analyze_job_fit(resume_text, ai_payload)
                    for j in batch:
                        j["match_score"] = scores_map.get(j["_temp_id"], 0)
                except Exception as e:
                    logger.error("AI batch scoring failed: %s", e)
                    for j in batch:
                        j["match_score"] = 0

            # Commit new jobs to DB
            for job_data in new_jobs:
                new_job = Job(
                    title=job_data["title"],
                    company=job_data["company"],
                    url=job_data["url"],
                    description=job_data.get("description", ""),
                    location=job_data.get("location", ""),
                    match_score=job_data.get("match_score", 0),
                    ats_source=job_data.get("ats_source", ""),
                    is_priority=job_data.get("is_priority", False),
                    status="discovered",
                    posted_at=job_data.get("posted_at", ""),
                    salary_range=job_data.get("salary_range", ""),
                    owner_id=user_id
                )
                db.add(new_job)

            db.commit()

        _update_status("Scan complete!", len(new_jobs))

        # --- 6. Return all jobs sorted by score ---
        all_jobs = db.query(Job).filter(Job.owner_id == user_id).order_by(
            Job.is_priority.desc(), Job.match_score.desc()
        ).all()
        return all_jobs, len(new_jobs)

    finally:
        if user_id in SCAN_STATUS:
            SCAN_STATUS[user_id]["is_scanning"] = False
        db.close()
