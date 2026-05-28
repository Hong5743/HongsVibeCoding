from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.company import Company, CompanyStatus
from app.services.company import public_company_card_dict, public_company_detail_dict

router = APIRouter(prefix="/public", tags=["public"])


def ok(data=None) -> dict:
    return {"success": True, "data": data, "error": None}


@router.get("/companies")
async def list_public_companies(
    db: AsyncSession = Depends(get_db),
    q: Optional[str] = Query(None, description="기업명 또는 소개 키워드 검색"),
    industry: Optional[str] = Query(None, description="업종 필터"),
    region: Optional[str] = Query(None, description="지역(주소) 필터"),
):
    stmt = select(Company).where(Company.status == CompanyStatus.approved)

    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            (Company.name.ilike(like)) | (Company.description.ilike(like))
        )
    if industry:
        stmt = stmt.where(Company.industry.ilike(f"%{industry}%"))
    if region:
        stmt = stmt.where(Company.address.ilike(f"%{region}%"))

    result = await db.execute(stmt)
    companies = list(result.scalars().all())
    return ok([public_company_card_dict(c) for c in companies])


@router.get("/companies/{company_id}")
async def get_public_company(company_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Company).where(
            Company.id == company_id,
            Company.status == CompanyStatus.approved,
        )
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "data": None, "error": "Company not found"},
        )
    return ok(public_company_detail_dict(company))
