"""
Simple test to verify the AI provider abstraction works correctly
"""
import asyncio
import os
from services.ai_provider import get_ai_provider
from core.config import AI_PROVIDER, GEMINI_API_KEY, QWEN_API_KEY, DEFAULT_MODEL_ID


async def test_ai_provider():
    print(f"Testing AI provider: {AI_PROVIDER}")
    
    # Initialize the AI provider based on configuration
    ai_provider_instance = get_ai_provider(
        provider_name=AI_PROVIDER,
        gemini_api_key=GEMINI_API_KEY,
        qwen_api_key=QWEN_API_KEY,
        model_id=DEFAULT_MODEL_ID
    )
    
    # Sample data for testing
    resume_text = "Experienced Software Engineer with expertise in Python, AI, and cloud technologies."
    job_description = "Looking for a Python developer with experience in AI and machine learning."
    
    print("\nTesting analyze_job_fit...")
    try:
        result = await ai_provider_instance.analyze_job_fit(resume_text, job_description)
        print(f"Success: {result}")
    except Exception as e:
        print(f"Error in analyze_job_fit: {e}")
    
    print("\nTesting generate_cover_letter...")
    try:
        cover_letter = await ai_provider_instance.generate_cover_letter(resume_text, job_description)
        print(f"Success: Generated {len(cover_letter)} characters")
    except Exception as e:
        print(f"Error in generate_cover_letter: {e}")
    
    print("\nTesting semantic_match_fields...")
    try:
        current_labels = ["First Name", "Last Name", "Email Address"]
        saved_labels = ["Given Name", "Surname", "Email"]
        matches = await ai_provider_instance.semantic_match_fields(current_labels, saved_labels)
        print(f"Success: {matches}")
    except Exception as e:
        print(f"Error in semantic_match_fields: {e}")


if __name__ == "__main__":
    asyncio.run(test_ai_provider())