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


# ── GET /api/public/companies?q= (keyword search) ────────────────────────────

@pytest.mark.asyncio
async def test_search_by_name_keyword(client: AsyncClient, db: AsyncSession):
    await _make_approved_company(db, "a1@test.com", "Alpha Corp")
    await _make_approved_company(db, "a2@test.com", "Beta Inc")
    res = await client.get(f"{BASE}/companies?q=alpha")
    data = res.json()["data"]
    assert len(data) == 1
    assert data[0]["name"] == "Alpha Corp"


@pytest.mark.asyncio
async def test_search_by_description_keyword(client: AsyncClient, db: AsyncSession):
    company = Company(
        email="desc@test.com",
        password_hash="hashed",
        is_verified=True,
        status=CompanyStatus.approved,
        name="DescCo",
        description="We build amazing software solutions",
    )
    db.add(company)
    await db.commit()

    res = await client.get(f"{BASE}/companies?q=amazing+software")
    data = res.json()["data"]
    assert len(data) == 1
    assert data[0]["name"] == "DescCo"


@pytest.mark.asyncio
async def test_search_returns_empty_when_no_match(client: AsyncClient, db: AsyncSession):
    await _make_approved_company(db)
    res = await client.get(f"{BASE}/companies?q=nonexistentkeyword12345")
    assert res.json()["data"] == []


@pytest.mark.asyncio
async def test_search_is_case_insensitive(client: AsyncClient, db: AsyncSession):
    await _make_approved_company(db, "case@test.com", "Seoul Technology")
    res = await client.get(f"{BASE}/companies?q=SEOUL")
    assert len(res.json()["data"]) == 1


# ── GET /api/public/companies?industry= (industry filter) ────────────────────

@pytest.mark.asyncio
async def test_filter_by_industry(client: AsyncClient, db: AsyncSession):
    await _make_approved_company(db, "it@test.com", "IT Corp", industry="IT")
    await _make_approved_company(db, "fin@test.com", "Fin Corp", industry="Finance")
    res = await client.get(f"{BASE}/companies?industry=IT")
    data = res.json()["data"]
    assert len(data) == 1
    assert data[0]["name"] == "IT Corp"


@pytest.mark.asyncio
async def test_filter_by_industry_case_insensitive(client: AsyncClient, db: AsyncSession):
    await _make_approved_company(db, "it2@test.com", "Tech Co", industry="Technology")
    res = await client.get(f"{BASE}/companies?industry=technology")
    assert len(res.json()["data"]) == 1


# ── GET /api/public/companies?region= (region filter) ────────────────────────

@pytest.mark.asyncio
async def test_filter_by_region(client: AsyncClient, db: AsyncSession):
    seoul = Company(
        email="seoul@test.com",
        password_hash="hashed",
        is_verified=True,
        status=CompanyStatus.approved,
        name="Seoul Corp",
        address="서울시 강남구",
    )
    busan = Company(
        email="busan@test.com",
        password_hash="hashed",
        is_verified=True,
        status=CompanyStatus.approved,
        name="Busan Corp",
        address="부산시 해운대구",
    )
    db.add_all([seoul, busan])
    await db.commit()

    res = await client.get(f"{BASE}/companies?region=서울")
    data = res.json()["data"]
    assert len(data) == 1
    assert data[0]["name"] == "Seoul Corp"


# ── Combined filters ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_combined_q_and_industry_filter(client: AsyncClient, db: AsyncSession):
    await _make_approved_company(db, "c1@test.com", "Seoul IT", industry="IT")
    await _make_approved_company(db, "c2@test.com", "Seoul Finance", industry="Finance")
    await _make_approved_company(db, "c3@test.com", "Busan IT", industry="IT")

    res = await client.get(f"{BASE}/companies?q=Seoul&industry=IT")
    data = res.json()["data"]
    assert len(data) == 1
    assert data[0]["name"] == "Seoul IT"


@pytest.mark.asyncio
async def test_no_filter_returns_all_approved(client: AsyncClient, db: AsyncSession):
    await _make_approved_company(db, "x1@test.com", "Corp A")
    await _make_approved_company(db, "x2@test.com", "Corp B")
    res = await client.get(f"{BASE}/companies")
    assert len(res.json()["data"]) == 2
