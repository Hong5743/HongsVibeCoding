import os

import httpx
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.company import Company, CompanyStatus

router = APIRouter(prefix="/chat", tags=["chat"])

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

MAX_MATCHED = 5
MAX_FALLBACK = 10
MAX_DESC_CHARS = 200
OLLAMA_TIMEOUT_S = 30.0

SYSTEM_PROMPT_MATCH = (
    "당신은 기업 소개 플랫폼의 AI 도우미입니다. "
    "아래 등록된 기업 정보를 바탕으로 사용자의 질문에 친절하게 답변하세요. "
    "등록된 기업 정보 외의 내용은 답변하지 마세요.\n\n"
    "[등록된 기업 정보]\n{context}"
)

SYSTEM_PROMPT_FALLBACK = (
    "당신은 기업 소개 플랫폼의 AI 도우미입니다. "
    "사용자가 질문한 기업과 직접 일치하는 기업은 플랫폼에 등록되어 있지 않습니다. "
    "아래는 현재 플랫폼에 등록된 다른 기업들입니다. "
    "이 기업들을 소개하거나, 직접 일치 기업이 없음을 안내하고 등록된 기업을 추천하세요.\n\n"
    "[등록된 기업 정보]\n{context}"
)


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


def ok(data=None) -> dict:
    return {"success": True, "data": data, "error": None}


def err(message: str) -> dict:
    return {"success": False, "data": None, "error": message}


def _build_context(companies: list[Company]) -> str:
    if not companies:
        return "현재 등록된 기업 정보가 없습니다."
    parts = []
    for c in companies:
        part = f"- {c.name}"
        if c.industry:
            part += f" (업종: {c.industry})"
        if c.address:
            part += f" / 위치: {c.address}"
        if c.description:
            part += f"\n  소개: {c.description[:MAX_DESC_CHARS]}"
        parts.append(part)
    return "\n".join(parts)


def _build_search_conditions(question: str):
    tokens = [t for t in question.split() if len(t) > 1]
    if not tokens:
        tokens = [question]
    conditions = []
    for token in tokens:
        like = f"%{token}%"
        conditions.append(Company.name.ilike(like))
        conditions.append(Company.description.ilike(like))
        conditions.append(Company.industry.ilike(like))
        conditions.append(Company.address.ilike(like))
    return or_(*conditions)


@router.post("")
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    # 토큰 기반 검색
    stmt = (
        select(Company)
        .where(Company.status == CompanyStatus.approved)
        .where(_build_search_conditions(req.question))
        .limit(MAX_MATCHED)
    )
    result = await db.execute(stmt)
    matched = list(result.scalars().all())
    is_fallback = False

    if not matched:
        is_fallback = True
        all_stmt = (
            select(Company)
            .where(Company.status == CompanyStatus.approved)
            .limit(MAX_FALLBACK)
        )
        all_result = await db.execute(all_stmt)
        matched = list(all_result.scalars().all())

    context = _build_context(matched)
    sources = [{"id": c.id, "name": c.name} for c in matched]

    prompt_template = SYSTEM_PROMPT_FALLBACK if is_fallback else SYSTEM_PROMPT_MATCH
    system_prompt = prompt_template.format(context=context)

    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT_S) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": req.question},
                    ],
                    "stream": False,
                },
            )
            response.raise_for_status()
            answer = response.json()["message"]["content"]
    except httpx.HTTPError:
        return JSONResponse(
            status_code=503,
            content=err("AI 서비스에 일시적으로 연결할 수 없습니다. 잠시 후 다시 시도해주세요."),
        )

    return ok({"answer": answer, "sources": sources})
