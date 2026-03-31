from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from database_dir import database
from api.schemas import JobStatusUpdateSchema
from api.dependencies import get_db, get_current_user
from core.logger_config import get_logger

logger = get_logger(__name__)
router = APIRouter()

from services.state import SCAN_STATUS

def _job_to_dict(j: database.Job) -> dict:
    return {
        "id": j.id,
        "title": j.title,
        "company": j.company,
        "url": j.url,
        "description": j.description,
        "location": j.location,
        "match_score": j.match_score,
        "ats_source": j.ats_source,
        "is_priority": j.is_priority,
        "status": j.status,
        "posted_at": j.posted_at,
        "salary_range": j.salary_range,
    }

@router.get("/scan/status")
async def get_scan_status(current_user: database.User = Depends(get_current_user)):
    status = SCAN_STATUS.get(current_user.id, {"is_scanning": False, "progress": ""})
    return status

@router.post("/scan")
async def scan_jobs(background_tasks: BackgroundTasks, current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    from services.scraper_service import discover_and_score_jobs
    from services.profile_manager import load_resume
    resume_text = load_resume(current_user.id)
    if not resume_text:
        raise HTTPException(status_code=400, detail="Resume text not found. Please upload a resume first.")
    
    # Initialize track state
    SCAN_STATUS[current_user.id] = {
        "is_scanning": True,
        "progress": "Starting job scan...",
        "discovered_count": 0
    }
    
    logger.info("Job scan triggered for user %d", current_user.id)
    background_tasks.add_task(discover_and_score_jobs, resume_text=resume_text, user_id=current_user.id)
    return {"status": "success", "message": "Job discovery started in background"}

@router.get("/stats")
async def job_stats(current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_count = db.query(database.Job).filter(database.Job.status == "discovered", database.Job.owner_id == current_user.id).count()
    applied_count = db.query(database.Job).filter(database.Job.status == "applied", database.Job.owner_id == current_user.id).count()
    return {
        "new": new_count,
        "applied": applied_count,
        "all": new_count + applied_count
    }

@router.get("")
async def list_jobs(status: str = "new", skip: int = 0, limit: int = 20, current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(database.Job).filter(database.Job.status != "hidden", database.Job.owner_id == current_user.id)
    if status == "new":
        query = query.filter(database.Job.status == "discovered")
    elif status == "applied":
        query = query.filter(database.Job.status == "applied")
        
    jobs = query.order_by(
        database.Job.is_priority.desc(),
        database.Job.match_score.desc()
    ).offset(skip).limit(limit).all()
    
    return [_job_to_dict(j) for j in jobs]

@router.put("/{job_id}/status")
async def update_job_status(job_id: int, request: Request, current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    body = await request.json()
    new_status = body.get("status")
    if new_status not in ("discovered", "applied", "hidden"):
        raise HTTPException(status_code=400, detail="Invalid status")
    job = db.query(database.Job).filter(database.Job.id == job_id, database.Job.owner_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.status = new_status
    db.commit()
    return _job_to_dict(job)
