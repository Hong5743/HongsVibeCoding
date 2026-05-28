# vibecoding 스택 패턴 참조

에이전트가 구현 시 따라야 할 이 프로젝트의 확립된 패턴.

---

## 백엔드 패턴

### 라우터 구조

```python
# backend/app/api/{module}.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.company import Company, CompanyStatus

router = APIRouter(prefix="/{module}", tags=["{module}"])

def ok(data=None) -> dict:
    return {"success": True, "data": data, "error": None}
```

### main.py 라우터 등록

```python
# backend/app/main.py
from app.api.{module} import router as {module}_router
app.include_router({module}_router, prefix="/api")
```

### SQLAlchemy async 쿼리

```python
# 단건 조회
result = await db.execute(select(Company).where(Company.id == company_id))
company = result.scalar_one_or_none()

# 목록 조회 + 필터
stmt = select(Company).where(Company.status == CompanyStatus.approved)
if q:
    stmt = stmt.where(Company.name.ilike(f"%{q}%"))
result = await db.execute(stmt)
companies = list(result.scalars().all())
```

### 테스트 패턴

```python
# backend/tests/test_{module}.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

BASE = "/api/{module}"

@pytest.mark.asyncio
async def test_{feature}(client: AsyncClient, db: AsyncSession):
    # Arrange
    # Act
    res = await client.post(f"{BASE}/endpoint", json={...})
    # Assert
    assert res.status_code == 200
    assert res.json()["success"] is True
```

### 인증 의존성

```python
from app.api.auth import get_current_company, get_current_admin

# 기업 로그인 필요
@router.get("/protected")
async def endpoint(company: Company = Depends(get_current_company)):
    ...

# 관리자 필요
@router.get("/admin-only")
async def endpoint(admin = Depends(get_current_admin)):
    ...
```

---

## 프론트엔드 패턴

### Composable 구조

```typescript
// frontend/composables/use{Feature}.ts
interface {Feature}Params { ... }

export function use{Feature}() {
  const config = useRuntimeConfig();
  const base = config.public.apiBase;

  async function fetch{Feature}(params?: {Feature}Params): Promise<Result[]> {
    const query: Record<string, string> = {};
    // params → query 변환
    const res = await $fetch<ApiResponse<Result[]>>(
      `${base}/api/{module}/endpoint`,
      { query }
    );
    return res.data;
  }

  return { fetch{Feature} };
}
```

### 페이지 패턴 (검색 포함)

```vue
<script setup lang="ts">
import { ref, watch } from "vue";
import { use{Feature} } from "~/composables/use{Feature}";

const { fetch{Feature} } = use{Feature}();
const searchQ = ref("");

const { data, pending, error, refresh } = await useAsyncData(
  "{unique-key}",
  () => fetch{Feature}({ q: searchQ.value || undefined })
);

let debounceTimer: ReturnType<typeof setTimeout> | null = null;
watch([searchQ], () => {
  if (debounceTimer) clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => refresh(), 300);
});
</script>
```

### 인증 store

```typescript
// Pinia store: stores/auth.ts
// useAuthStore().token — JWT access token
// useAuthStore().isLoggedIn — boolean
// middleware/auth.ts — 보호 페이지 리다이렉트
```

---

## 환경 변수

```env
# backend/.env
DATABASE_URL=sqlite+aiosqlite:///./dev.db
SECRET_KEY=...
OLLAMA_BASE_URL=http://localhost:11434  # AI Chat용
```

```typescript
// nuxt.config.ts → runtimeConfig.public.apiBase
// 기본값: http://localhost:8000
```
