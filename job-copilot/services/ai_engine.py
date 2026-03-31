from typing import Dict, Any, List
import json
from core.config import AI_PROVIDER, GEMINI_API_KEY, QWEN_API_KEY, DEFAULT_MODEL_ID, AI_BASE_URL
from services.ai_provider import get_ai_provider

# Initialize the AI provider based on configuration
ai_provider = get_ai_provider(
    provider_name=AI_PROVIDER,
    gemini_api_key=GEMINI_API_KEY,
    qwen_api_key=QWEN_API_KEY,
    model_id=DEFAULT_MODEL_ID,
    base_url=AI_BASE_URL
)

async def analyze_job_fit(resume_text: str, job_description: str) -> Dict[str, Any]:
    return await ai_provider.analyze_job_fit(resume_text, job_description)

async def batch_analyze_job_fit(resume_text: str, jobs: List[Dict[str, str]]) -> Dict[str, int]:
    """Takes a list of jobs with 'id' and 'description' keys, returns {id: score}"""
    # Exclude empty descriptions to save tokens
    valid_jobs = [j for j in jobs if j.get("description")]
    if not valid_jobs:
        return {}
    jobs_json = json.dumps(valid_jobs)
    return await ai_provider.batch_analyze_job_fit(resume_text, jobs_json)

async def generate_cover_letter(resume_text: str, job_description: str) -> str:
    return await ai_provider.generate_cover_letter(resume_text, job_description)

async def semantic_match_fields(current_labels: List[str], saved_labels: List[str]) -> Dict[str, str]:
    """
    Matches current form labels to saved labels using the configured AI provider.
    """
    return await ai_provider.semantic_match_fields(current_labels, saved_labels)

async def get_company_domains(company_names: List[str]) -> Dict[str, str]:
    """
    Batch fetches corporate domains for a list of company names.
    """
    return await ai_provider.get_company_domains(company_names)

async def compress_resume(resume_text: str) -> str:
    """Uses AI to compress and optimize raw resume text"""
    return await ai_provider.compress_resume(resume_text)


