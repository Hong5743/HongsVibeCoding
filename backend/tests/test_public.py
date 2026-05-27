import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company, CompanyStatus

BASE = "/api/public"
AUTH = "/api/auth"
ADMIN = "/api/admin"


async def _make_approved_company(
    db: AsyncSession,
    email: str = "approved@test.com",
    name: str = "Test Corp",
    industry: str = "Technology",
) -> Company:
    company = Company(
        email=email,
        password_hash="hashed",
        is_verified=True,
        status=CompanyStatus.approved,
        name=name,
        description="A test company",
        industry=industry,
        company_size="50-100",
        address="Seoul, Korea",
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


async def _make_pending_company(db: AsyncSession, email: str = "pending@test.com") -> Company:
    company = Company(
        email=email,
        password_hash="hashed",
        is_verified=True,
        status=CompanyStatus.pending,
        name="Pending Corp",
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


async def _make_rejected_company(db: AsyncSession, email: str = "rejected@test.com") -> Company:
    company = Company(
        email=email,
        password_hash="hashed",
        is_verified=True,
        status=CompanyStatus.rejected,
        name="Rejected Corp",
        rejection_reason="Not qualified",
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


# ── GET /api/public/companies ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_public_companies_no_auth_required(client: AsyncClient, db: AsyncSession):
    await _make_approved_company(db)
    res = await client.get(f"{BASE}/companies")
    assert res.status_code == 200
    assert res.json()["success"] is True


@pytest.mark.asyncio
async def test_list_public_companies_only_approved(client: AsyncClient, db: AsyncSession):
    await _make_approved_company(db, "a@test.com", "Approved Corp")
    await _make_pending_company(db, "p@test.com")
    await _make_rejected_company(db, "r@test.com")

    res = await client.get(f"{BASE}/companies")
    data = res.json()["data"]
    assert len(data) == 1
    assert data[0]["name"] == "Approved Corp"


@pytest.mark.asyncio
async def test_list_public_companies_empty(client: AsyncClient, db: AsyncSession):
    res = await client.get(f"{BASE}/companies")
    assert res.status_code == 200
    assert res.json()["data"] == []


@pytest.mark.asyncio
async def test_list_public_companies_card_fields(client: AsyncClient, db: AsyncSession):
    await _make_approved_company(db)
    res = await client.get(f"{BASE}/companies")
    card = res.json()["data"][0]
    expected_keys = {"id", "name", "logo_url", "description", "industry", "company_size", "address"}
    assert set(card.keys()) == expected_keys


@pytest.mark.asyncio
async def test_list_public_companies_no_sensitive_fields(client: AsyncClient, db: AsyncSession):
    await _make_approved_company(db)
    res = await client.get(f"{BASE}/companies")
    card = res.json()["data"][0]
    assert "email" not in card
    assert "password_hash" not in card
    assert "rejection_reason" not in card


@pytest.mark.asyncio
async def test_list_public_companies_multiple(client: AsyncClient, db: AsyncSession):
    await _make_approved_company(db, "a1@test.com", "Alpha")
    await _make_approved_company(db, "a2@test.com", "Beta")
    res = await client.get(f"{BASE}/companies")
    assert len(res.json()["data"]) == 2


# ── GET /api/public/companies/{id} ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_public_company_success(client: AsyncClient, db: AsyncSession):
    company = await _make_approved_company(db)
    res = await client.get(f"{BASE}/companies/{company.id}")
    assert res.status_code == 200
    assert res.json()["success"] is True
    assert res.json()["data"]["id"] == company.id


@pytest.mark.asyncio
async def test_get_public_company_detail_fields(client: AsyncClient, db: AsyncSession):
    company = await _make_approved_company(db)
    res = await client.get(f"{BASE}/companies/{company.id}")
    detail = res.json()["data"]
    expected_keys = {
        "id", "name", "logo_url", "description", "industry",
        "founded_year", "employee_count", "company_size",
        "website", "contact_email", "phone", "address",
        "image_urls", "instagram_url", "linkedin_url",
    }
    assert set(detail.keys()) == expected_keys


@pytest.mark.asyncio
async def test_get_public_company_no_sensitive_fields(client: AsyncClient, db: AsyncSession):
    company = await _make_approved_company(db)
    res = await client.get(f"{BASE}/companies/{company.id}")
    detail = res.json()["data"]
    assert "email" not in detail
    assert "password_hash" not in detail
    assert "rejection_reason" not in detail


@pytest.mark.asyncio
async def test_get_public_company_not_found(client: AsyncClient, db: AsyncSession):
    res = await client.get(f"{BASE}/companies/9999")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_get_public_company_pending_returns_404(client: AsyncClient, db: AsyncSession):
    company = await _make_pending_company(db)
    res = await client.get(f"{BASE}/companies/{company.id}")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_get_public_company_rejected_returns_404(client: AsyncClient, db: AsyncSession):
    company = await _make_rejected_company(db)
    res = await client.get(f"{BASE}/companies/{company.id}")
    assert res.status_code == 404
