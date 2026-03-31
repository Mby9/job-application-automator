import os
from dotenv import load_dotenv

load_dotenv()

# AI Provider Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")  # Options: gemini, openai, etc.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
DEFAULT_MODEL_ID = os.getenv("DEFAULT_MODEL_ID", "gemini-3.1-flash-lite-preview")

DATABASE_URL = "sqlite:///./data/job_automator.db"
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))
SCREENS_DIR = "screenshots"
OUTPUT_DIR = "outputs"

