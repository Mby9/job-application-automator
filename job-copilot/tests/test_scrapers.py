import asyncio
from scrapers.greenhouse import scrape_greenhouse
from scrapers.lever import scrape_lever
from scrapers.ashby import scrape_ashby

async def main():
    # Greenhouse - try a known active token
    jobs = await scrape_greenhouse("openai", "OpenAI")
    print(f"Greenhouse (openai): {len(jobs)} jobs")
    if jobs:
        print(f"  Sample: {jobs[0]['title']} @ {jobs[0]['location']}")

    # Lever
    jobs2 = await scrape_lever("reddit", "Reddit")
    print(f"Lever (reddit): {len(jobs2)} jobs")
    if jobs2:
        print(f"  Sample: {jobs2[0]['title']} @ {jobs2[0]['location']}")

    # Ashby
    jobs3 = await scrape_ashby("ashby", "Ashby")
    print(f"Ashby (ashby): {len(jobs3)} jobs")
    if jobs3:
        print(f"  Sample: {jobs3[0]['title']} @ {jobs3[0]['location']}")

asyncio.run(main())
