import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company, CompanyStatus

BASE = "/api/chat"


async def _make_approved_company(
    db: AsyncSession,
    email: str = "chat@test.com",
    name: str = "Chat Corp",
    industry: str = "IT",
    address: str = "서울시 강남구",
    description: str = "AI 기반 솔루션 기업",
) -> Company:
    company = Company(
        email=email,
        password_hash="hashed",
        is_verified=True,
        status=CompanyStatus.approved,
        name=name,
        industry=industry,
        address=address,
        description=description,
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


def _mock_ollama_response(content: str = "테스트 답변입니다."):
    mock_response = MagicMock()
    mock_response.json.return_value = {"message": {"content": content}}
    mock_response.raise_for_status = MagicMock()
    return mock_response


# ── POST /api/chat ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_chat_success(client: AsyncClient, db: AsyncSession):
    await _make_approved_company(db)

    with patch("app.api.chat.httpx.AsyncClient") as mock_client_class:
        mock_instance = AsyncMock()
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_instance.post = AsyncMock(return_value=_mock_ollama_response("IT 스타트업 정보입니다."))

        res = await client.post(BASE, json={"question": "IT 스타트업 알려줘"})

    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "answer" in data["data"]
    assert "sources" in data["data"]


@pytest.mark.asyncio
async def test_chat_returns_sources(client: AsyncClient, db: AsyncSession):
    company = await _make_approved_company(db, name="Seoul Tech")

    with patch("app.api.chat.httpx.AsyncClient") as mock_client_class:
        mock_instance = AsyncMock()
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_instance.post = AsyncMock(return_value=_mock_ollama_response())

        res = await client.post(BASE, json={"question": "Seoul Tech 알려줘"})

    sources = res.json()["data"]["sources"]
    assert any(s["id"] == company.id for s in sources)


@pytest.mark.asyncio
async def test_chat_no_companies_still_responds(client: AsyncClient, db: AsyncSession):
    with patch("app.api.chat.httpx.AsyncClient") as mock_client_class:
        mock_instance = AsyncMock()
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_instance.post = AsyncMock(return_value=_mock_ollama_response("등록된 기업이 없습니다."))

        res = await client.post(BASE, json={"question": "아무 질문"})

    assert res.status_code == 200
    assert res.json()["success"] is True


@pytest.mark.asyncio
async def test_chat_missing_question(client: AsyncClient, db: AsyncSession):
    res = await client.post(BASE, json={})
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_chat_ollama_error_returns_503(client: AsyncClient, db: AsyncSession):
    import httpx as httpx_lib

    with patch("app.api.chat.httpx.AsyncClient") as mock_client_class:
        mock_instance = AsyncMock()
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_instance.post = AsyncMock(
            side_effect=httpx_lib.ConnectError("Connection refused")
        )

        res = await client.post(BASE, json={"question": "질문"})

    assert res.status_code == 503
    body = res.json()
    assert body["success"] is False
    assert body["data"] is None
    assert "연결할 수 없습니다" in body["error"]


@pytest.mark.asyncio
async def test_chat_question_too_long(client: AsyncClient, db: AsyncSession):
    res = await client.post(BASE, json={"question": "가" * 501})
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_chat_fallback_uses_all_companies(client: AsyncClient, db: AsyncSession):
    await _make_approved_company(db, "c1@test.com", "Busan Corp", industry="제조", address="부산시")
    await _make_approved_company(db, "c2@test.com", "Daegu Corp", industry="금융", address="대구시")

    with patch("app.api.chat.httpx.AsyncClient") as mock_client_class:
        mock_instance = AsyncMock()
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_instance.post = AsyncMock(return_value=_mock_ollama_response("관련 기업이 없지만 다른 기업을 소개합니다."))

        res = await client.post(BASE, json={"question": "zzzzzz_없는기업"})

    assert res.status_code == 200
    # fallback: 매치 없어도 sources에 전체 기업 포함
    sources = res.json()["data"]["sources"]
    assert len(sources) == 2


@pytest.mark.asyncio
async def test_chat_token_search_matches_partial(client: AsyncClient, db: AsyncSession):
    await _make_approved_company(db, "t1@test.com", "Seoul AI", industry="IT", address="서울시")

    with patch("app.api.chat.httpx.AsyncClient") as mock_client_class:
        mock_instance = AsyncMock()
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_instance.post = AsyncMock(return_value=_mock_ollama_response("Seoul AI 기업입니다."))

        # 공백으로 분리된 토큰 검색
        res = await client.post(BASE, json={"question": "서울 IT 스타트업"})

    assert res.status_code == 200
    sources = res.json()["data"]["sources"]
    assert any(s["name"] == "Seoul AI" for s in sources)
