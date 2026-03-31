from fastapi import APIRouter, Depends, Request, UploadFile, File, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from database_dir import database
from api.schemas import UserProfileSchema, PreferencesSchema
from api.dependencies import get_db, get_current_user
from core.logger_config import get_logger
import json
from api.logging_route import LoggingRoute

logger = get_logger(__name__)
router = APIRouter(route_class=LoggingRoute)

@router.get("")
async def get_profile(current_user: database.User = Depends(get_current_user)):
    from services.profile_manager import load_profile
    profile = load_profile(current_user.id)
    if not profile:
        return {}
    return profile.dict()

@router.post("")
async def save_profile(profile: UserProfileSchema, current_user: database.User = Depends(get_current_user)):
    from services.profile_manager import save_profile, UserProfile
    from services.ai_engine import compress_resume
    
    profile_dict = profile.dict()
    if profile_dict.get("resume_text"):
        logger.info("Compressing resume for user %d during profile save", current_user.id)
        profile_dict["resume_text"] = await compress_resume(profile_dict["resume_text"])
        
    profile_data = UserProfile(**profile_dict)
    save_profile(current_user.id, profile_data)
    return {"status": "success"}

@router.get("/resume")
async def get_resume(current_user: database.User = Depends(get_current_user)):
    from services.profile_manager import load_resume
    resume = load_resume(current_user.id)
    return {"resume_text": resume}

@router.put("/resume")
async def update_resume(request: Request, current_user: database.User = Depends(get_current_user)):
    body = await request.json()
    resume_text = body.get("resume_text", "")
    
    from services.ai_engine import compress_resume
    logger.info("Compressing resume for user %d during manual resume update", current_user.id)
    compressed_text = await compress_resume(resume_text)
    
    from services.profile_manager import load_profile, save_profile, UserProfile
    profile = load_profile(current_user.id)
    if not profile:
        profile = UserProfile(
            full_name=current_user.username,
            email=f"{current_user.username}@example.com",
            phone="",
            linkedin_url="",
            portfolio_url="",
            resume_text=compressed_text
        )
    else:
        profile.resume_text = compressed_text
    save_profile(current_user.id, profile)
    return {"status": "success"}
