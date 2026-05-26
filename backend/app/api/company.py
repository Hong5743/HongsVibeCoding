from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.company import Company
from app.schemas.company import ProfileUpdateRequest
from app.services import auth as auth_service
from app.services import company as company_service

router = APIRouter(prefix="/companies", tags=["companies"])
bearer = HTTPBearer()


def ok(data=None) -> dict:
    return {"success": True, "data": data, "error": None}


async def _current_company(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> Company:
    try:
        return await auth_service.get_current_company(db, credentials.credentials)
    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail={"success": False, "data": None, "error": str(e)},
        )


@router.get("/me")
async def get_profile(company: Company = Depends(_current_company)):
    return ok(company_service.company_to_dict(company))


@router.put("/me")
async def update_profile(
    req: ProfileUpdateRequest,
    db: AsyncSession = Depends(get_db),
    company: Company = Depends(_current_company),
):
    updated = await company_service.update_profile(db, company, req.model_dump(exclude_unset=True))
    return ok(company_service.company_to_dict(updated))


@router.post("/me/upload")
async def upload_images(
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    company: Company = Depends(_current_company),
):
    urls = []
    for file in files:
        try:
            url = await company_service.save_upload(file)
            urls.append(url)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail={"success": False, "data": None, "error": str(e)},
            )

    existing = company.image_urls or []
    updated = await company_service.update_profile(db, company, {"image_urls": existing + urls})
    return ok({"urls": urls, "all_image_urls": updated.image_urls})
