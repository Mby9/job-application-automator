from pydantic import BaseModel
from typing import List, Optional

class FieldMappingSchema(BaseModel):
    label_text: str
    field_value: str
    category: Optional[str] = None
    status: Optional[str] = "pending"

class MappingStatusUpdateSchema(BaseModel):
    status: str

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class UserProfileSchema(BaseModel):
    full_name: str
    email: str
    phone: str
    linkedin_url: str
    portfolio_url: str
    resume_text: str
    preferred_locations: List[str] = []
    preferred_keywords: List[str] = []
    remote_only: bool = False
    legal_work_country: str = "Any"

class PreferencesSchema(BaseModel):
    preferred_locations: List[str] = []
    preferred_keywords: List[str] = []
    remote_only: bool = False
    dark_mode: bool = False
    seniority_level: str = "Any"
    legal_work_country: str = "Any"

class CompanyUpdateSchema(BaseModel):
    status: Optional[str] = None
    is_priority: Optional[bool] = None

class CompanyAddSchema(BaseModel):
    name: str
    ats_type: str
    board_token: str
    status: str = "approved"
    is_priority: bool = False

class JobStatusUpdateSchema(BaseModel):
    status: str

class ResumeUpdate(BaseModel):
    resume_text: str
