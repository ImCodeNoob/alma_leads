from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models import LeadStatus


class LeadOut(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    resume_filename: str
    status: LeadStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeadStatusUpdate(BaseModel):
    status: LeadStatus


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
