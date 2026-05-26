from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.admin import Admin
from app.models.company import CompanyStatus
from app.schemas.admin import AdminLoginRequest, RejectRequest
from app.services import admin as admin_service
from app.services.auth import get_company_by_id

router = APIRouter(prefix="/admin", tags=["admin"])
bearer = HTTPBearer()


def ok(data=None) -> dict:
    return {"success": True, "data": data, "error": None}


async def _current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> Admin:
    try:
        return await admin_service.get_current_admin(db, credentials.credentials)
    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail={"success": False, "data": None, "error": str(e)},
        )


async def _get_company_or_404(company_id: int, db: AsyncSession):
    company = await get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "data": None, "error": "Company not found"},
        )
    return company


@router.post("/login")
async def login(req: AdminLoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        token = await admin_service.login(db, req.email, req.password)
    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail={"success": False, "data": None, "error": str(e)},
        )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/companies")
async def list_companies(
    status: CompanyStatus | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(_current_admin),
):
    companies = await admin_service.list_companies(db, status)
    return ok([admin_service.company_to_admin_dict(c) for c in companies])


@router.get("/companies/{company_id}")
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(_current_admin),
):
    company = await _get_company_or_404(company_id, db)
    return ok(admin_service.company_to_admin_dict(company))


@router.put("/companies/{company_id}/approve")
async def approve_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(_current_admin),
):
    company = await _get_company_or_404(company_id, db)
    updated = await admin_service.approve_company(db, company)
    return ok(admin_service.company_to_admin_dict(updated))


@router.put("/companies/{company_id}/reject")
async def reject_company(
    company_id: int,
    req: RejectRequest,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(_current_admin),
):
    company = await _get_company_or_404(company_id, db)
    updated = await admin_service.reject_company(db, company, req.reason)
    return ok(admin_service.company_to_admin_dict(updated))


@router.delete("/companies/{company_id}")
async def delete_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(_current_admin),
):
    company = await _get_company_or_404(company_id, db)
    await admin_service.delete_company(db, company)
    return ok({"message": f"Company {company_id} deleted"})
