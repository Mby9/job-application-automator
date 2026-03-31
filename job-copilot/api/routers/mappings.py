from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database_dir import database
from api.schemas import FieldMappingSchema, MappingStatusUpdateSchema
from api.dependencies import get_db, get_current_user
from core.logger_config import get_logger
from api.logging_route import LoggingRoute

logger = get_logger(__name__)
router = APIRouter(route_class=LoggingRoute)

@router.post("/save-field")
async def save_field(mapping: FieldMappingSchema, current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        db_mapping = db.query(database.FieldMapping).filter(
            database.FieldMapping.label_text == mapping.label_text,
            database.FieldMapping.owner_id == current_user.id
        ).first()
        if db_mapping:
            db_mapping.field_value = mapping.field_value
            db_mapping.category = mapping.category
        else:
            db_mapping = database.FieldMapping(
                label_text=mapping.label_text,
                field_value=mapping.field_value,
                category=mapping.category,
                status="active",
                owner_id=current_user.id
            )
            db.add(db_mapping)
        db.commit()
        return {"status": "success"}
    except Exception as e:
        logger.error("Failed to save field for user %d: %s", current_user.id, e)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-fill-values")
async def get_fill_values(current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    mappings = db.query(database.FieldMapping).filter(database.FieldMapping.owner_id == current_user.id).all()
    return {m.label_text: m.field_value for m in mappings}

@router.post("/match-fields")
async def match_fields(request: Request, current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    body = await request.json()
    current_labels = body.get("labels", [])
    saved_mappings = db.query(database.FieldMapping).filter(
        database.FieldMapping.status == "active",
        database.FieldMapping.owner_id == current_user.id
    ).all()
    if not saved_mappings:
        return {}
    saved_labels_list = [m.label_text for m in saved_mappings]
    saved_values_map = {m.label_text: m.field_value for m in saved_mappings}
    
    # Merge profile data if available
    from services.profile_manager import load_profile
    profile = load_profile(current_user.id)
    if profile:
        profile_data = {
            "Full Name": profile.full_name,
            "Email": profile.email,
            "Phone Number": profile.phone,
            "LinkedIn URL": profile.linkedin_url,
            "Portfolio URL": profile.portfolio_url
        }
        for label, val in profile_data.items():
            if val and label not in saved_values_map:
                saved_labels_list.append(label)
                saved_values_map[label] = val
    try:
        from services.semantic_matcher import HybridSemanticMatcher
        matcher = HybridSemanticMatcher(db)
        matches = await matcher.match_fields(current_labels, saved_labels_list)
        result = {cur: saved_values_map[saved] for cur, saved in matches.items() if saved in saved_values_map}
        return result
    except Exception as e:
        logger.error("Field matching failed: %s", e)
        return {}

@router.get("/mappings")
async def get_all_mappings(current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(database.FieldMapping).filter(database.FieldMapping.owner_id == current_user.id).order_by(database.FieldMapping.status.desc(), database.FieldMapping.id.desc()).all()

@router.post("/mappings")
async def create_mapping(mapping: FieldMappingSchema, current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        new_mapping = database.FieldMapping(
            label_text=mapping.label_text,
            field_value=mapping.field_value,
            category=mapping.category,
            status=mapping.status,
            owner_id=current_user.id
        )
        db.add(new_mapping)
        db.commit()
        db.refresh(new_mapping)
        return new_mapping
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/mappings/{mapping_id}/status")
async def update_mapping_status(mapping_id: int, update: MappingStatusUpdateSchema, current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    mapping = db.query(database.FieldMapping).filter(database.FieldMapping.id == mapping_id, database.FieldMapping.owner_id == current_user.id).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    mapping.status = update.status
    db.commit()
    return {"status": "success"}

@router.delete("/mappings/{mapping_id}")
async def delete_mapping(mapping_id: int, current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    mapping = db.query(database.FieldMapping).filter(database.FieldMapping.id == mapping_id, database.FieldMapping.owner_id == current_user.id).first()
    if mapping:
        db.delete(mapping)
        db.commit()
    return {"status": "deleted"}
