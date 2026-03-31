import json
import os
from typing import List
from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    full_name: str
    email: str
    phone: str
    linkedin_url: str
    portfolio_url: str
    resume_text: str
    preferred_locations: List[str] = Field(default_factory=list)
    preferred_keywords: List[str] = Field(default_factory=list)
    remote_only: bool = False

PROFILE_DIR = "data/profiles"

def get_profile_path(user_id: int) -> str:
    if not os.path.exists(PROFILE_DIR):
        os.makedirs(PROFILE_DIR, exist_ok=True)
    return os.path.join(PROFILE_DIR, f"user_{user_id}.json")

def save_profile(user_id: int, profile: UserProfile):
    with open(get_profile_path(user_id), "w") as f:
        json.dump(profile.dict(), f, indent=4)

def load_profile(user_id: int) -> UserProfile:
    path = get_profile_path(user_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            return UserProfile(**data)
    # Fallback to legacy if single-user existed (optional, but good for migration)
    LEGACY_FILE = "data/user_profile.json"
    if user_id == 1 and os.path.exists(LEGACY_FILE):
        with open(LEGACY_FILE, "r") as f:
            data = json.load(f)
            return UserProfile(**data)
    return None

def load_resume(user_id: int) -> str:
    profile = load_profile(user_id)
    return profile.resume_text if profile else ""
