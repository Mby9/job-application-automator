from core.logger_config import setup_logging
# Set up logging immediately before any other project imports
setup_logging()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
import uvicorn
from database_dir.database import init_db, SessionLocal, User
from core.logger_config import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Job-Copilot API started")
    
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from services.scraper_service import discover_and_score_jobs
    from services import profile_manager
    
    scheduler = AsyncIOScheduler()
    
    async def scheduled_discovery():
        logger.info("Running scheduled background discovery for all users...")
        db = SessionLocal()
        try:
            users = db.query(User).filter(User.is_active == True).all()
            for user in users:
                logger.info(f"Discovery for user: {user.username} (ID: {user.id})")
                resume_text = profile_manager.load_resume(user.id)
                if resume_text:
                    try:
                        await discover_and_score_jobs(resume_text=resume_text, user_id=user.id)
                    except Exception as e:
                        logger.error(f"Discovery failed for user {user.username}: {e}")
                else:
                    logger.warning(f"No resume found for user {user.username}, skipping discovery.")
        except Exception as e:
            logger.error(f"Scheduled discovery orchestration failed: {e}")
        finally:
            db.close()
            
    # Run every 6 hours
    scheduler.add_job(scheduled_discovery, 'interval', hours=6)
    scheduler.start()
    
    yield
    
    scheduler.shutdown()
    logger.info("Job-Copilot API shutting down")

app = FastAPI(title="Job-Copilot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for extension/frontend compatibility
    allow_credentials=False, # Must be False if allow_origins is wildcard
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Moved HTTP Request/Response body logging to api/logging_route.py using a native stream wrapper.

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Import and include Routers
from api.routers import auth, mappings, companies, jobs, profile, preferences, utils

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(mappings.router, prefix="/api", tags=["Mappings"])
app.include_router(companies.router, prefix="/api/companies", tags=["Companies"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(preferences.router, prefix="/api/preferences", tags=["Preferences"])
app.include_router(utils.router, prefix="/api/utils", tags=["Utils"])

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
