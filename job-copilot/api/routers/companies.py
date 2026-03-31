from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database_dir import database
from api.schemas import CompanyAddSchema, CompanyUpdateSchema
from api.dependencies import get_db, get_current_user
from core.logger_config import get_logger
from api.logging_route import LoggingRoute
import json
import asyncio

logger = get_logger(__name__)
router = APIRouter(route_class=LoggingRoute)

def _company_to_dict(c: database.Company) -> dict:
    return {
        "id": c.id,
        "name": c.name,
        "ats_type": c.ats_type,
        "board_token": c.board_token,
        "source_url": c.source_url,
        "status": c.status,
        "is_priority": c.is_priority,
        "domain": c.domain,
        "logo_url": c.logo_url
    }

def _fetch_domains_background(company_ids: list[int]):
    if not company_ids:
        return
    db = database.SessionLocal()
    try:
        from services.ai_engine import get_company_domains
        db_companies = db.query(database.Company).filter(database.Company.id.in_(company_ids)).all()
        names = [c.name for c in db_companies]
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            domain_mapping = loop.run_until_complete(get_company_domains(names))
        finally:
            loop.close()

        for c in db_companies:
            if c.name in domain_mapping and domain_mapping[c.name]:
                domain = domain_mapping[c.name]
                c.domain = domain
                c.logo_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
        db.commit()
    except Exception as e:
        logger.error(f"Background domain fetch failed: {e}")
    finally:
        db.close()

@router.get("")
async def list_companies(current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    companies = db.query(database.Company).filter(database.Company.owner_id == current_user.id).all()
    return [_company_to_dict(c) for c in companies]

@router.post("")
async def add_company(payload: CompanyAddSchema, current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(database.Company).filter(
        database.Company.board_token == payload.board_token,
        database.Company.ats_type == payload.ats_type,
        database.Company.owner_id == current_user.id
    ).first()
    if existing:
        return _company_to_dict(existing)
    company = database.Company(**payload.dict(), owner_id=current_user.id)
    db.add(company)
    db.commit()
    db.refresh(company)
    return _company_to_dict(company)

@router.put("/{company_id}")
async def update_company(company_id: int, payload: CompanyUpdateSchema, current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    company = db.query(database.Company).filter(database.Company.id == company_id, database.Company.owner_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if payload.status is not None:
        company.status = payload.status
    if payload.is_priority is not None:
        company.is_priority = payload.is_priority
    db.commit()
    return _company_to_dict(company)

@router.delete("/{company_id}")
async def delete_company(company_id: int, current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    company = db.query(database.Company).filter(database.Company.id == company_id, database.Company.owner_id == current_user.id).first()
    if company:
        db.delete(company)
        db.commit()
    return {"status": "deleted"}

from fastapi import UploadFile, File
import csv
import io

@router.post("/batch-import")
async def batch_import_companies(background_tasks: BackgroundTasks, file: UploadFile = File(...), current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        contents = await file.read()
        decoded = contents.decode("utf-8-sig")
        reader = csv.reader(io.StringIO(decoded))
        
        added_ids = []
        skipped = 0
        for row in reader:
            if not row or not row[0].strip():
                continue
            c_name = row[0].strip()
            
            existing = db.query(database.Company).filter(
                database.Company.name.ilike(c_name),
                database.Company.owner_id == current_user.id
            ).first()
            if existing:
                skipped += 1
                if not existing.domain:
                    added_ids.append(existing.id)
                continue
                
            new_company = database.Company(
                name=c_name,
                ats_type="unknown",
                board_token=c_name.lower().replace(" ", ""),
                status="approved",
                owner_id=current_user.id
            )
            db.add(new_company)
            db.flush()
            added_ids.append(new_company.id)

        db.commit()
        if added_ids:
            background_tasks.add_task(_fetch_domains_background, added_ids)

        return {"status": "success", "added": len(added_ids), "skipped_due_to_duplicate": skipped}
    except Exception as e:
        logger.exception("CSV upload failed")
        raise HTTPException(status_code=500, detail=str(e))

DISCOVERY_STATUS = {}

def _run_discovery_background(user_id: int, keywords: list, locations: list):
    DISCOVERY_STATUS[user_id] = True
    db = database.SessionLocal()
    try:
        from services.company_discovery import discover_companies
        logger.info("Starting background company discovery for user %d | keywords=%s | locations=%s", user_id, keywords, locations)
        
        # discover_companies is synchronous
        found = discover_companies(keywords, locations)

        new_companies = []
        for c in found:
            existing = db.query(database.Company).filter(
                database.Company.board_token == c["board_token"],
                database.Company.ats_type == c["ats_type"],
                database.Company.owner_id == user_id
            ).first()
            if not existing:
                row = database.Company(
                    name=c["name"],
                    ats_type=c["ats_type"],
                    board_token=c["board_token"],
                    source_url=c.get("source_url"),
                    status="suggested",
                    is_priority=False,
                    owner_id=user_id
                )
                db.add(row)
                new_companies.append(row)

        db.commit()
        for row in new_companies:
            db.refresh(row)

        if new_companies:
            added_ids = [r.id for r in new_companies]
            _fetch_domains_background(added_ids)
            
    except Exception as e:
        logger.error(f"Background discovery failed for user {user_id}: {e}")
    finally:
        DISCOVERY_STATUS[user_id] = False
        db.close()

@router.post("/discover")
async def discover_companies_endpoint(background_tasks: BackgroundTasks, current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if DISCOVERY_STATUS.get(current_user.id):
        return {"status": "already_running"}
        
    # Clear existing 'suggested' companies before starting the new discovery
    db.query(database.Company).filter(
        database.Company.owner_id == current_user.id,
        database.Company.status == "suggested"
    ).delete()
    db.commit()
        
    prefs_row = db.query(database.UserPreferences).filter(database.UserPreferences.owner_id == current_user.id).first()
    keywords = json.loads(prefs_row.preferred_keywords or "[]") if prefs_row else []
    locations = json.loads(prefs_row.preferred_locations or "[]") if prefs_row else []

    background_tasks.add_task(_run_discovery_background, current_user.id, keywords, locations)
    
    return {"status": "started"}

@router.get("/discover/status")
async def get_discovery_status(current_user: database.User = Depends(get_current_user)):
    is_running = DISCOVERY_STATUS.get(current_user.id, False)
    return {"is_discovering": is_running}
