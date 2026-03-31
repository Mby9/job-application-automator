from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database_dir import database
from api.schemas import PreferencesSchema
from api.dependencies import get_db, get_current_user
from core.logger_config import get_logger
import json
from api.logging_route import LoggingRoute

logger = get_logger(__name__)
router = APIRouter(route_class=LoggingRoute)

@router.get("")
async def get_preferences(current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.query(database.UserPreferences).filter(database.UserPreferences.owner_id == current_user.id).first()
    if not row:
        return PreferencesSchema().dict()
    return {
        "preferred_locations": json.loads(row.preferred_locations or "[]"),
        "preferred_keywords": json.loads(row.preferred_keywords or "[]"),
        "remote_only": row.remote_only or False,
        "dark_mode": row.dark_mode or False,
        "seniority_level": row.seniority_level or "Any",
    }

@router.put("")
async def save_preferences(prefs: PreferencesSchema, current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.query(database.UserPreferences).filter(database.UserPreferences.owner_id == current_user.id).first()
    if not row:
        row = database.UserPreferences(owner_id=current_user.id)
        db.add(row)
    row.preferred_locations = json.dumps(prefs.preferred_locations)
    row.preferred_keywords = json.dumps(prefs.preferred_keywords)
    row.remote_only = prefs.remote_only
    row.dark_mode = prefs.dark_mode
    row.seniority_level = prefs.seniority_level
    db.commit()
    logger.info("Preferences saved for user %d: locations=%s, keywords=%s, remote_only=%s, dark_mode=%s, seniority=%s",
                current_user.id, prefs.preferred_locations, prefs.preferred_keywords, prefs.remote_only, prefs.dark_mode, prefs.seniority_level)
    return {"status": "saved"}
