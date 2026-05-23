from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    ResetPasswordRequest,
    SignupRequest,
    TokenResponse,
)
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer()


def ok(data: dict | None = None) -> dict:
    return {"success": True, "data": data, "error": None}


def err(msg: str) -> HTTPException:
    return HTTPException(status_code=400, detail={"success": False, "data": None, "error": msg})


@router.post("/signup", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def signup(req: SignupRequest, db: AsyncSession = Depends(get_db)):
    try:
        company, token = await auth_service.signup(db, req.email, req.password)
    except ValueError as e:
        raise HTTPException(status_code=409, detail={"success": False, "data": None, "error": str(e)})

    # TODO: send email with token — for dev, return token in response
    return ok({"message": "Verification email sent.", "debug_token": token})


@router.get("/verify-email", response_model=MessageResponse)
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    try:
        await auth_service.verify_email(db, token)
    except ValueError as e:
        raise err(str(e))
    return ok({"message": "Email verified successfully."})


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        access_token, refresh_token = await auth_service.login(db, req.email, req.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail={"success": False, "data": None, "error": str(e)})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=MessageResponse)
async def refresh(req: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        access_token = await auth_service.refresh_access_token(db, req.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail={"success": False, "data": None, "error": str(e)})
    return ok({"access_token": access_token})


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(req: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    token = await auth_service.forgot_password(db, req.email)
    # Always return 200 to avoid email enumeration
    data: dict = {"message": "If the email exists, a reset link has been sent."}
    if token:
        data["debug_token"] = token  # TODO: remove in production, send via email
    return ok(data)


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(req: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    try:
        await auth_service.reset_password(db, req.token, req.new_password)
    except ValueError as e:
        raise err(str(e))
    return ok({"message": "Password reset successfully."})


@router.get("/me", response_model=MessageResponse)
async def me(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
):
    try:
        company = await auth_service.get_current_company(db, credentials.credentials)
    except ValueError as e:
        raise HTTPException(status_code=401, detail={"success": False, "data": None, "error": str(e)})
    return ok({"id": company.id, "email": company.email, "is_verified": company.is_verified, "status": company.status})
