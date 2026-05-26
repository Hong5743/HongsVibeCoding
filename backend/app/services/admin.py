from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.admin import Admin
from app.models.company import Company, CompanyStatus
from app.services.auth import decode_token, get_company_by_id, hash_password, verify_password

ALGORITHM = "HS256"


def create_admin_access_token(admin_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(admin_id), "type": "admin_access", "exp": expire},
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def company_to_admin_dict(company: Company) -> dict:
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
        "rejection_reason": company.rejection_reason,
        "created_at": company.created_at.isoformat() if company.created_at else None,
        "updated_at": company.updated_at.isoformat() if company.updated_at else None,
    }


async def get_admin_by_email(db: AsyncSession, email: str) -> Admin | None:
    result = await db.execute(select(Admin).where(Admin.email == email))
    return result.scalar_one_or_none()


async def get_admin_by_id(db: AsyncSession, admin_id: int) -> Admin | None:
    result = await db.execute(select(Admin).where(Admin.id == admin_id))
    return result.scalar_one_or_none()


async def login(db: AsyncSession, email: str, password: str) -> str:
    admin = await get_admin_by_email(db, email)
    if not admin or not verify_password(password, admin.password_hash):
        raise ValueError("Invalid email or password")
    return create_admin_access_token(admin.id)


async def get_current_admin(db: AsyncSession, token: str) -> Admin:
    try:
        payload = decode_token(token)
    except JWTError:
        raise ValueError("Invalid token")
    if payload.get("type") != "admin_access":
        raise ValueError("Invalid token type")
    admin = await get_admin_by_id(db, int(payload["sub"]))
    if not admin:
        raise ValueError("Admin not found")
    return admin


async def list_companies(
    db: AsyncSession, status: CompanyStatus | None = None
) -> list[Company]:
    q = select(Company)
    if status is not None:
        q = q.where(Company.status == status)
    result = await db.execute(q)
    return list(result.scalars().all())


async def approve_company(db: AsyncSession, company: Company) -> Company:
    company.status = CompanyStatus.approved
    company.rejection_reason = None
    await db.commit()
    await db.refresh(company)
    return company


async def reject_company(db: AsyncSession, company: Company, reason: str) -> Company:
    company.status = CompanyStatus.rejected
    company.rejection_reason = reason
    await db.commit()
    await db.refresh(company)
    return company


async def delete_company(db: AsyncSession, company: Company) -> None:
    await db.delete(company)
    await db.commit()


async def create_admin(db: AsyncSession, email: str, password: str) -> Admin:
    admin = Admin(email=email, password_hash=hash_password(password))
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    return admin
