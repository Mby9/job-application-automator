import asyncio
from services.scraper import scrape_job
from services.ai_engine import analyze_job_fit, generate_cover_letter
from services.profile_manager import load_profile

async def main():
    profile = load_profile()
    if not profile:
        print("Please create a user_profile.json first.")
        return

    job_url = input("Enter Job URL to analyze: ")
    print(f"Scraping {job_url}...")
    job_data = await scrape_job(job_url)
    
    print("Analyzing fit...")
    analysis = await analyze_job_fit(profile.resume_text, job_data['content'])
    print("\n--- Analysis ---")
    print(analysis)
    
    print("\nGenerating tailored cover letter...")
    cover_letter = await generate_cover_letter(profile.resume_text, job_data['content'])
    print("\n--- Cover Letter ---")
    print(cover_letter)
    
    # Save to file
    with open("tailored_application.txt", "w") as f:
        f.write(f"JOB: {job_data['title']}\nURL: {job_url}\n\n")
        f.write("--- ANALYSIS ---\n")
        f.write(analysis)
        f.write("\n\n--- COVER LETTER ---\n")
        f.write(cover_letter)
    print("\nResults saved to tailored_application.txt")

if __name__ == "__main__":
    asyncio.run(main())
