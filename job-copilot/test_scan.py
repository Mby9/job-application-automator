import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from database_dir.database import SessionLocal, User, Company, Job
from services.scraper_service import discover_and_score_jobs
from services.profile_manager import save_profile, UserProfile

async def main():
    db = SessionLocal()
    # Need to clean up any old dummy companies we create
    try:
        alice = db.query(User).filter(User.username == "alice").first()
        if not alice:
            print("Alice not found! Please run the signup script first.")
            return
        
        # Profile creation
        profile = UserProfile(
            full_name="Alice Candidate",
            email="alice@example.com",
            phone="555-0101",
            linkedin_url="x",
            portfolio_url="y",
            resume_text="Senior backend engineer specializing in Python, FastAPI, and data scraping.",
            preferred_locations=["Remote"],
            preferred_keywords=["Engineer", "Software", "Python"],
            remote_only=False
        )
        save_profile(alice.id, profile)
        print("Set up Alice profile with test resume.")

        # Ensure approved company exists
        comp = db.query(Company).filter(Company.owner_id == alice.id, Company.status == "approved").first()
        if not comp:
            comp = Company(name="TestCorp", ats_type="lever", board_token="netflix", status="approved", owner_id=alice.id)
            db.add(comp)
            db.commit()
            print("Added Netflix as dummy 'lever' company to scan.")
        
        print(f"Running discover_and_score_jobs for user_id={alice.id}...")
        jobs, new_count = await discover_and_score_jobs(profile.resume_text, alice.id)
        
        print(f"Scan returned successfully! new jobs: {new_count}")
        print(f"Total jobs for user returned: {len(jobs)}")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
