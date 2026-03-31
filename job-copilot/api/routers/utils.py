from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from database_dir import database
from api.dependencies import get_current_user
from core.logger_config import get_logger
from services.resume_parser import parse_resume_file
from api.logging_route import LoggingRoute

logger = get_logger(__name__)
router = APIRouter(route_class=LoggingRoute)

@router.post("/parse-resume")
async def parse_resume_endpoint(file: UploadFile = File(...), current_user: database.User = Depends(get_current_user)):
    try:
        contents = await file.read()
        text = parse_resume_file(contents, file.filename)
        
        # Proactively compress the parsed text
        from services.ai_engine import compress_resume
        logger.info("Compressing parsed resume text for user %d", current_user.id)
        compressed_text = await compress_resume(text)
        
        return {"text": compressed_text}
    except Exception as e:
        logger.error(f"Error parsing uploaded resume: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse the uploaded file.")
