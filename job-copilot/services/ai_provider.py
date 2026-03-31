"""
Abstract AI Provider interface to allow switching between different AI services
like Google Gemini, Qwen, OpenAI, etc.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from core.prompts import ANALYZE_JOB_FIT_PROMPT, GENERATE_COVER_LETTER_PROMPT, SEMANTIC_MATCH_FIELDS_PROMPT, GET_COMPANY_DOMAINS_PROMPT, RESUME_COMPRESSION_PROMPT
from core.logger_config import get_logger

logger = get_logger(__name__)


class AIProvider(ABC):
    """Abstract base class for AI providers using Template Method for uniform logging"""
    
    async def execute_prompt(self, prompt: str, expect_json: bool = False) -> str:
        """Centralized logging wrapper for all AI calls"""
        logger.info(f"AI Input:\n{prompt}\n---")
        try:
            response_text = await self._generate_content(prompt, expect_json)
            logger.info(f"AI Output:\n{response_text}\n===")
            return response_text
        except Exception as e:
            logger.error(f"AI Error:\n{e}\n===")
            raise

    @abstractmethod
    async def _generate_content(self, prompt: str, expect_json: bool) -> str:
        """Actual API call to be implemented by subclass"""
        pass

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        import json
        import re
        try:
            return json.loads(response_text)
        except Exception:
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise

    async def analyze_job_fit(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Analyze job fit and return match score, missing skills, and summary"""
        prompt = ANALYZE_JOB_FIT_PROMPT.format(resume_text=resume_text, job_description=job_description)
        try:
            response_text = await self.execute_prompt(prompt, expect_json=True)
            return self._parse_json_response(response_text)
        except Exception as e:
            return {"match_score": 0, "missing_skills": [], "summary": f"Error: {e}"}

    async def batch_analyze_job_fit(self, resume_text: str, jobs_json: str) -> Dict[str, int]:
        """Analyze multiple jobs and return a dictionary mapping `id` to an integer match score"""
        from core.prompts import ANALYZE_BATCH_JOB_FIT_PROMPT
        prompt = ANALYZE_BATCH_JOB_FIT_PROMPT.format(resume_text=resume_text, jobs_json=jobs_json)
        try:
            response_text = await self.execute_prompt(prompt, expect_json=True)
            return self._parse_json_response(response_text)
        except Exception as e:
            return {}
    
    async def generate_cover_letter(self, resume_text: str, job_description: str) -> str:
        """Generate a cover letter based on resume and job description"""
        prompt = GENERATE_COVER_LETTER_PROMPT.format(resume_text=resume_text, job_description=job_description)
        try:
            return await self.execute_prompt(prompt, expect_json=False)
        except Exception as e:
            return f"Error: {e}"
    
    async def semantic_match_fields(self, current_labels: List[str], saved_labels: List[str]) -> Dict[str, str]:
        """Match current form labels to saved labels using semantic similarity"""
        if not saved_labels:
            return {}
        prompt = SEMANTIC_MATCH_FIELDS_PROMPT.format(current_labels=current_labels, saved_labels=saved_labels)
        try:
            response_text = await self.execute_prompt(prompt, expect_json=True)
            return self._parse_json_response(response_text)
        except Exception as e:
            return {}

    async def get_company_domains(self, company_names: List[str]) -> Dict[str, str]:
        """Fetch the primary website domains for a list of companies"""
        if not company_names:
            return {}
        prompt = GET_COMPANY_DOMAINS_PROMPT.format(company_names="\n".join(company_names))
        try:
            response_text = await self.execute_prompt(prompt, expect_json=True)
            return self._parse_json_response(response_text)
        except Exception as e:
            return {}

    async def compress_resume(self, resume_text: str) -> str:
        """Uses AI to compress and optimize raw resume text"""
        from core.prompts import RESUME_COMPRESSION_PROMPT
        prompt = RESUME_COMPRESSION_PROMPT.format(resume_text=resume_text)
        try:
            return await self.execute_prompt(prompt, expect_json=False)
        except Exception as e:
            logger.error(f"Resume compression failed: {e}")
            return resume_text # Fallback to raw if AI fails

class GeminiProvider(AIProvider):
    """Google Gemini AI provider implementation"""
    
    def __init__(self, api_key: str, model_id: str = "gemini-3.1-flash-lite-preview"):
        from google import genai
        self.client = genai.Client(api_key=api_key)
        self.model_id = model_id

    async def _generate_content(self, prompt: str, expect_json: bool) -> str:
        config = {'response_mime_type': 'application/json'} if expect_json else None
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=config
        )
        return response.text


class OpenAICompatibleProvider(AIProvider):
    """Generic OpenAI-compatible provider (Qwen, DeepSeek, etc.)"""
    
    def __init__(self, api_key: str, base_url: str, model_id: str):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model_id = model_id

    async def _generate_content(self, prompt: str, expect_json: bool) -> str:
        response_format = {"type": "json_object"} if expect_json and "gemini" not in self.model_id.lower() else None
        response = await self.client.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}],
            response_format=response_format
        )
        return response.choices[0].message.content


def get_ai_provider(provider_name: str, **kwargs) -> AIProvider:
    """Factory function to get the appropriate AI provider"""
    name = provider_name.lower()
    if name == "gemini":
        api_key = kwargs.get("gemini_api_key") or kwargs.get("api_key")
        model_id = kwargs.get("model_id", "gemini-3.1-flash-lite-preview")
        return GeminiProvider(api_key=api_key, model_id=model_id)
    elif name in ["openai", "qwen"]:
        api_key = kwargs.get("qwen_api_key") or kwargs.get("api_key")
        model_id = kwargs.get("model_id", "qwen-plus")
        base_url = kwargs.get("base_url") or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        return OpenAICompatibleProvider(api_key=api_key, base_url=base_url, model_id=model_id)
    else:
        raise ValueError(f"Unsupported AI provider: {provider_name}")
