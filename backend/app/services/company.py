import os
import uuid

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company

UPLOAD_DIR = "uploads"
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def company_to_dict(company: Company) -> dict:
    return {
        "id": company.id,
        "email": company.email,
        "is_verified": company.is_verified,
        "status": company.status,
        "name": company.name,
        "logo_url": company.logo_url,
        "description": company.description,
        "industry": company.industry,
        "founded_year": company.founded_year,
        "employee_count": company.employee_count,
        "company_size": company.company_size,
        "website": company.website,
        "contact_email": company.contact_email,
        "phone": company.phone,
        "address": company.address,
        "image_urls": company.image_urls,
        "instagram_url": company.instagram_url,
        "linkedin_url": company.linkedin_url,
    }


async def update_profile(db: AsyncSession, company: Company, fields: dict) -> Company:
    for key, value in fields.items():
        setattr(company, key, value)
    await db.commit()
    await db.refresh(company)
    return company


async def save_upload(file: UploadFile) -> str:
    content_type = file.content_type or ""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(
            f"Unsupported file type: {content_type!r}. Allowed: jpeg, png, webp, gif"
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise ValueError("File too large. Maximum size is 5MB")

    raw_name = file.filename or "upload"
    ext = raw_name.rsplit(".", 1)[-1].lower() if "." in raw_name else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as f:
        f.write(content)

    return f"/uploads/{filename}"
