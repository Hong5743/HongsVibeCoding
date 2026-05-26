from typing import Optional
from pydantic import BaseModel


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    founded_year: Optional[int] = None
    employee_count: Optional[int] = None
    company_size: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    instagram_url: Optional[str] = None
    linkedin_url: Optional[str] = None
