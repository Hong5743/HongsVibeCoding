import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.company import Company
from app.models.token import EmailVerificationToken, PasswordResetToken

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(company_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": str(company_id), "type": "access", "exp": expire}, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token(company_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    return jwt.encode({"sub": str(company_id), "type": "refresh", "exp": expire}, settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])


async def get_company_by_email(db: AsyncSession, email: str) -> Company | None:
    result = await db.execute(select(Company).where(Company.email == email))
    return result.scalar_one_or_none()


async def get_company_by_id(db: AsyncSession, company_id: int) -> Company | None:
    result = await db.execute(select(Company).where(Company.id == company_id))
    return result.scalar_one_or_none()


async def signup(db: AsyncSession, email: str, password: str) -> tuple[Company, str]:
    existing = await get_company_by_email(db, email)
    if existing:
        raise ValueError("Email already registered")

    company = Company(email=email, password_hash=hash_password(password))
    db.add(company)
    await db.flush()

    token_value = str(uuid.uuid4())
    verify_token = EmailVerificationToken(
        company_id=company.id,
        token=token_value,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    db.add(verify_token)
    await db.commit()
    await db.refresh(company)

    return company, token_value


async def verify_email(db: AsyncSession, token: str) -> Company:
    result = await db.execute(
        select(EmailVerificationToken).where(EmailVerificationToken.token == token)
    )
    verify_token = result.scalar_one_or_none()

    if not verify_token:
        raise ValueError("Invalid verification token")
    if verify_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise ValueError("Verification token expired")

    company = await get_company_by_id(db, verify_token.company_id)
    if not company:
        raise ValueError("Company not found")

    company.is_verified = True
    await db.delete(verify_token)
    await db.commit()
    await db.refresh(company)
    return company


async def login(db: AsyncSession, email: str, password: str) -> tuple[str, str]:
    company = await get_company_by_email(db, email)
    if not company or not verify_password(password, company.password_hash):
        raise ValueError("Invalid email or password")
    if not company.is_verified:
        raise ValueError("Email not verified. Please check your inbox.")

    return create_access_token(company.id), create_refresh_token(company.id)


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> str:
    try:
        payload = decode_token(refresh_token)
    except JWTError:
        raise ValueError("Invalid refresh token")

    if payload.get("type") != "refresh":
        raise ValueError("Invalid token type")

    company_id = int(payload["sub"])
    company = await get_company_by_id(db, company_id)
    if not company:
        raise ValueError("Company not found")

    return create_access_token(company_id)


async def forgot_password(db: AsyncSession, email: str) -> str | None:
    company = await get_company_by_email(db, email)
    if not company:
        return None

    token_value = str(uuid.uuid4())
    reset_token = PasswordResetToken(
        company_id=company.id,
        token=token_value,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db.add(reset_token)
    await db.commit()
    return token_value


async def reset_password(db: AsyncSession, token: str, new_password: str) -> None:
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == token,
            PasswordResetToken.used == False,  # noqa: E712
        )
    )
    reset_token = result.scalar_one_or_none()

    if not reset_token:
        raise ValueError("Invalid or already used reset token")
    if reset_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise ValueError("Reset token expired")

    company = await get_company_by_id(db, reset_token.company_id)
    if not company:
        raise ValueError("Company not found")

    company.password_hash = hash_password(new_password)
    reset_token.used = True
    await db.commit()


async def get_current_company(db: AsyncSession, token: str) -> Company:
    try:
        payload = decode_token(token)
    except JWTError:
        raise ValueError("Invalid token")

    if payload.get("type") != "access":
        raise ValueError("Invalid token type")

    company = await get_company_by_id(db, int(payload["sub"]))
    if not company:
        raise ValueError("Company not found")
    return company
