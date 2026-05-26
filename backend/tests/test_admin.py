import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin
from app.services.auth import hash_password

AUTH = "/api/auth"
BASE = "/api/admin"


async def _create_admin(db: AsyncSession, email="admin@test.com", password="adminpass123") -> None:
    admin = Admin(email=email, password_hash=hash_password(password))
    db.add(admin)
    await db.commit()


async def _admin_token(client: AsyncClient, db: AsyncSession) -> str:
    await _create_admin(db)
    res = await client.post(f"{BASE}/login", json={"email": "admin@test.com", "password": "adminpass123"})
    return res.json()["access_token"]


async def _company_token(client: AsyncClient, email: str) -> str:
    signup = await client.post(f"{AUTH}/signup", json={"email": email, "password": "password123"})
    vtoken = signup.json()["data"]["debug_token"]
    await client.get(f"{AUTH}/verify-email", params={"token": vtoken})
    login = await client.post(f"{AUTH}/login", json={"email": email, "password": "password123"})
    return login.json()["access_token"]


# ── login ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_admin_login_success(client: AsyncClient, db: AsyncSession):
    await _create_admin(db)
    res = await client.post(f"{BASE}/login", json={"email": "admin@test.com", "password": "adminpass123"})
    assert res.status_code == 200
    assert "access_token" in res.json()


@pytest.mark.asyncio
async def test_admin_login_wrong_password(client: AsyncClient, db: AsyncSession):
    await _create_admin(db)
    res = await client.post(f"{BASE}/login", json={"email": "admin@test.com", "password": "wrongpass"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_company_token_rejected_on_admin_endpoint(client: AsyncClient, db: AsyncSession):
    """Company JWT must not grant access to admin endpoints."""
    company_token = await _company_token(client, "notadmin@test.com")
    res = await client.get(f"{BASE}/companies", headers={"Authorization": f"Bearer {company_token}"})
    assert res.status_code == 401


# ── list companies ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_companies(client: AsyncClient, db: AsyncSession):
    token = await _admin_token(client, db)
    await _company_token(client, "c1@test.com")
    await _company_token(client, "c2@test.com")

    res = await client.get(f"{BASE}/companies", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    companies = res.json()["data"]
    assert len(companies) == 2


@pytest.mark.asyncio
async def test_list_companies_filter_by_status(client: AsyncClient, db: AsyncSession):
    token = await _admin_token(client, db)
    await _company_token(client, "pending@test.com")

    res = await client.get(
        f"{BASE}/companies",
        params={"status": "pending"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert all(c["status"] == "pending" for c in res.json()["data"])


@pytest.mark.asyncio
async def test_list_companies_unauthenticated(client: AsyncClient):
    res = await client.get(f"{BASE}/companies")
    assert res.status_code == 403


# ── get single company ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_company_detail(client: AsyncClient, db: AsyncSession):
    token = await _admin_token(client, db)
    await _company_token(client, "detail@test.com")

    companies = (await client.get(f"{BASE}/companies", headers={"Authorization": f"Bearer {token}"})).json()["data"]
    cid = companies[0]["id"]

    res = await client.get(f"{BASE}/companies/{cid}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["id"] == cid
    assert "rejection_reason" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_company_not_found(client: AsyncClient, db: AsyncSession):
    token = await _admin_token(client, db)
    res = await client.get(f"{BASE}/companies/99999", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 404


# ── approve ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_approve_company(client: AsyncClient, db: AsyncSession):
    token = await _admin_token(client, db)
    await _company_token(client, "approve@test.com")

    companies = (await client.get(f"{BASE}/companies", headers={"Authorization": f"Bearer {token}"})).json()["data"]
    cid = companies[0]["id"]

    res = await client.put(f"{BASE}/companies/{cid}/approve", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["status"] == "approved"
    assert data["rejection_reason"] is None


# ── reject ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_reject_company(client: AsyncClient, db: AsyncSession):
    token = await _admin_token(client, db)
    await _company_token(client, "reject@test.com")

    companies = (await client.get(f"{BASE}/companies", headers={"Authorization": f"Bearer {token}"})).json()["data"]
    cid = companies[0]["id"]

    res = await client.put(
        f"{BASE}/companies/{cid}/reject",
        json={"reason": "Incomplete profile information"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["status"] == "rejected"
    assert data["rejection_reason"] == "Incomplete profile information"


@pytest.mark.asyncio
async def test_approve_clears_rejection_reason(client: AsyncClient, db: AsyncSession):
    token = await _admin_token(client, db)
    await _company_token(client, "reapprove@test.com")

    companies = (await client.get(f"{BASE}/companies", headers={"Authorization": f"Bearer {token}"})).json()["data"]
    cid = companies[0]["id"]

    await client.put(f"{BASE}/companies/{cid}/reject", json={"reason": "Bad"}, headers={"Authorization": f"Bearer {token}"})
    res = await client.put(f"{BASE}/companies/{cid}/approve", headers={"Authorization": f"Bearer {token}"})
    assert res.json()["data"]["rejection_reason"] is None
    assert res.json()["data"]["status"] == "approved"


# ── delete ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_company(client: AsyncClient, db: AsyncSession):
    token = await _admin_token(client, db)
    await _company_token(client, "delete@test.com")

    companies = (await client.get(f"{BASE}/companies", headers={"Authorization": f"Bearer {token}"})).json()["data"]
    cid = companies[0]["id"]

    res = await client.delete(f"{BASE}/companies/{cid}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200

    res2 = await client.get(f"{BASE}/companies/{cid}", headers={"Authorization": f"Bearer {token}"})
    assert res2.status_code == 404


@pytest.mark.asyncio
async def test_filter_approved_after_actions(client: AsyncClient, db: AsyncSession):
    token = await _admin_token(client, db)
    await _company_token(client, "f1@test.com")
    await _company_token(client, "f2@test.com")

    companies = (await client.get(f"{BASE}/companies", headers={"Authorization": f"Bearer {token}"})).json()["data"]
    await client.put(f"{BASE}/companies/{companies[0]['id']}/approve", headers={"Authorization": f"Bearer {token}"})

    approved = (await client.get(f"{BASE}/companies", params={"status": "approved"}, headers={"Authorization": f"Bearer {token}"})).json()["data"]
    pending = (await client.get(f"{BASE}/companies", params={"status": "pending"}, headers={"Authorization": f"Bearer {token}"})).json()["data"]

    assert len(approved) == 1
    assert len(pending) == 1
