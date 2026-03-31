"""
Programmatic job filter engine — no AI involved.
Filters jobs by location and title keywords, then flags/sorts priority companies.
"""
from typing import List, Dict, Any


def _location_matches(job_location: str, preferred_locations: List[str], remote_only: bool, legal_work_country: str = "Any") -> bool:
    """Returns True if the job location matches any of the user's preferred locations and legal work country."""
    loc = (job_location or "").lower()
    work_country = (legal_work_country or "Any").lower()

    # If a specific country is required, ensure it matches
    if work_country != "any":
        # If the location mentions another country, reject it.
        # This is basic; in a real app, we might use a library or AI, 
        # but for now we check for common non-matching country strings.
        countries = ["usa", "united states", "canada", "uk", "united kingdom", "india", "germany"]
        for c in countries:
            if c != work_country and (f" {c} " in f" {loc} " or loc.endswith(f" {c}") or loc.startswith(f"{c} ")):
                # If the job mentions a different country (e.g. Remote-USA and user is Canada), reject it.
                return False

    if not preferred_locations and not remote_only:
        return True  # No location preference set — accept everything

    # Always accept explicitly remote roles if they didn't fail the country check above
    if "remote" in loc:
        return True

    if remote_only:
        return False  # remote_only=True and job is not remote

    for preferred in preferred_locations:
        if preferred.lower() in loc:
            return True

    return False


def _keyword_matches(job_title: str, preferred_keywords: List[str]) -> bool:
    """Returns True if the job title contains any of the user's preferred keywords."""
    if not preferred_keywords:
        return True  # No keyword preference — accept everything

    title = (job_title or "").lower()
    for keyword in preferred_keywords:
        if keyword.lower() in title:
            return True

    return False


def _seniority_matches(job_title: str, target_seniority: str) -> bool:
    """Returns True if the job's inferred seniority does not clash with the target."""
    if not target_seniority or target_seniority.lower() == "any":
        return True

    title = (job_title or "").lower()
    target = target_seniority.lower()

    if target == "junior" or target == "intern":
        clash_words = ["senior", "sr", "lead", "staff", "principal", "manager", "head", "director", "vp", "president", "chief"]
        for word in clash_words:
            if f" {word} " in f" {title} ":
                return False
                
    elif target in ["senior", "lead", "staff", "manager", "director"]:
        clash_words = ["intern", "internship", "junior", "jr", "student", "entry"]
        for word in clash_words:
            if f" {word} " in f" {title} ":
                return False

    return True


def filter_jobs(
    jobs: List[Dict[str, Any]],
    preferred_locations: List[str],
    preferred_keywords: List[str],
    remote_only: bool,
    priority_companies: List[str],
    seniority_level: str = "Any",
) -> List[Dict[str, Any]]:
    """
    Filters a list of raw job dicts:
    1. Location match (case-insensitive substring)
    2. Keyword match on title
    3. Flags priority companies with is_priority=True
    4. Sorts priority company jobs to the top

    Args:
        jobs: List of RawJob dicts from scrapers
        preferred_locations: e.g. ["Toronto", "Remote"]
        preferred_keywords: e.g. ["AI Engineer", "Python"]
        remote_only: If True, only remote jobs pass
        priority_companies: Company names to boost to top

    Returns:
        Filtered and sorted list of job dicts
    """
    priority_names_lower = {c.lower() for c in priority_companies}
    filtered = []

    for job in jobs:
        if not _location_matches(job.get("location", ""), preferred_locations, remote_only):
            continue
        if not _seniority_matches(job.get("title", ""), seniority_level):
            continue
        if not _keyword_matches(job.get("title", ""), preferred_keywords):
            continue

        # Flag priority companies
        company_name = (job.get("company") or "").lower()
        job["is_priority"] = company_name in priority_names_lower
        filtered.append(job)

    # Sort: priority companies first, then by original order
    filtered.sort(key=lambda j: (not j.get("is_priority", False),))

    return filtered
