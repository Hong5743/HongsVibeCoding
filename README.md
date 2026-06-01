# Company Discovery Platform — 기업 소개 플랫폼

## 한줄 소개:
다양한 직군의 기업이 자신들을 소개하는 글을 등록하고, 방문자가 이를 보고 서로 거레처가 되는 바이브 코딩 웹 플랫폼. 

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| 기업 인증 | JWT (Access + Refresh Token) + 이메일 인증 |
| 기업 프로필 | CRUD + 관리자 승인 워크플로우 (pending → approved / rejected) |
| 관리자 패널 | 승인/거절/삭제, 거절 사유 입력 |
| 검색 & 필터 | 키워드 · 업종 · 지역 필터 (PostgreSQL Full-Text Search) |
| AI 챗봇 | 자연어 질의 → RAG 파이프라인 → Ollama 응답 |

---

## 기술 스택 & 선택 이유

### Frontend — Nuxt.js 3 + Tailwind CSS

**선택 이유:** 기업 프로필 페이지는 검색 노출이 핵심. Nuxt의 SSR/SSG로 크롤러가 완전한 HTML을 받을 수 있어 SEO에 유리. Vue 3 Composition API + Pinia로 auth 상태를 클라이언트 전역 관리.

**사용한 기술:**
- `useFetch` / `useAsyncData` — SSR 환경에서 서버사이드 데이터 패칭
- Pinia — auth store (토큰 저장, 로그인 상태 전역 공유)
- Nuxt Middleware — 인증 가드 (기업 대시보드, 관리자 페이지 접근 제어)

### Backend — FastAPI (Python)

**선택 이유:** 비동기 I/O로 Ollama API 호출 대기 중 다른 요청 처리 가능. Pydantic으로 요청/응답 스키마를 코드로 정의하면 자동으로 OpenAPI 문서 생성. Python 생태계라 LLM 연동 라이브러리가 풍부.

**사용한 기술:**
- Pydantic v2 — 입력 유효성 검증 + 응답 직렬화
- SQLAlchemy 2.0 (async) — ORM, 관계형 쿼리
- Alembic — DB 마이그레이션 버전 관리
- `python-jose` + `passlib[bcrypt]` — JWT 발급/검증, 비밀번호 해싱
- `python-multipart` — 이미지 파일 업로드 처리

### Database — PostgreSQL 16 (Docker)

**선택 이유:** Full-Text Search (`tsvector` / `to_tsquery`)가 내장되어 별도 검색 엔진 없이 한국어 포함 키워드 검색 구현 가능. 로컬 Docker 환경과 프로덕션 환경이 동일한 DB를 사용해 환경 차이 제거.

**사용한 기술:**
- `tsvector` 컬럼 인덱싱 — 기업명·소개·업종 Full-Text Search
- ENUM 타입 — `CompanyStatus` (pending / approved / rejected)
- UUID primary key — 파일명 충돌 방지 + 예측 불가 ID

### AI — Ollama (llama3.1:8b) + RAG

**선택 이유:** 외부 API 비용 없이 로컬에서 LLM 실행 가능. GPU 없는 환경에서도 동작하며, 추후 Gemini / Groq API로 교체 시 엔드포인트 URL만 변경하면 됨.

**RAG 파이프라인:**
```
사용자 질문
  → PostgreSQL Full-Text Search로 관련 기업 검색
  → 검색된 프로필 데이터를 프롬프트 컨텍스트로 구성
  → Ollama llama3.1:8b에 질문 + 컨텍스트 전달
  → 생성된 답변 반환
```

---

## 아키텍처

```
┌─────────────────┐     HTTP/JSON      ┌──────────────────────┐
│  Nuxt.js 3      │ ←────────────────→ │  FastAPI             │
│  (SSR, Pinia)   │                    │  ├── Auth API        │
└─────────────────┘                    │  ├── Company API     │
                                       │  ├── Admin API       │
                                       │  ├── Public API      │
                                       │  └── Chat API (RAG)  │
                                       └──────────┬───────────┘
                                                  │
                                    ┌─────────────┴──────────┐
                                    │  PostgreSQL 16          │
                                    │  (Docker)               │
                                    └─────────────┬──────────┘
                                                  │ RAG context
                                       ┌──────────┴──────────┐
                                       │  Ollama             │
                                       │  (llama3.1:8b)      │
                                       └─────────────────────┘
```

---

## Claude Code 멀티 에이전트 개발 파이프라인

이 프로젝트는 **Claude Code**의 스킬과 서브 에이전트를 활용해 이슈 단위로 자동 개발되었다.

### 서브 에이전트


### `issue-dev` 스킬 — 오케스트레이터

GitHub 이슈 번호를 입력하면 분석 → 백엔드 → 프론트엔드 → 코드 리뷰 → 커밋까지 파이프라인을 자동 실행.

```
Phase 0: 컨텍스트 확인 (_workspace/ 캐시 체크)
    │
    ▼
Phase 1: PRD.md 분석 → issue{N}_plan.md 저장
    │
    ▼
Phase 2: backend-dev 에이전트 호출 (TDD)
    │         └─ tests/ 작성(RED) → 구현(GREEN) → 전체 테스트 통과
    │         └─ issue{N}_api_contract.md 저장
    ▼
Phase 3: frontend-dev 에이전트 호출
    │         └─ api_contract.md 읽고 composable + 페이지 구현
    ▼
Phase 4: code-reviewer 에이전트 호출
    │         └─ APPROVED → Phase 5 / BLOCKED → 해당 에이전트 재호출
    ▼
Phase 5: git commit "feat: #{N} ..."
```

**사용 시점:** 이슈 #2(Auth) ~ #8(AI Chat) 전 이슈. 각 이슈마다 `issue-dev` 스킬 트리거 → 3개 에이전트 순차 실행.

---

### 서브 에이전트 역할 분담

**1. 기획 에이전트**
a) 시스템 설계
- mattpocock의 grill-me 스킬을 사용하여 시스템의 구조를 파악한다.
- mattpocock의 to-prd 스킬을 사용하여 파악된 시스템 구조를 토대로 요구사항을 문서로 남긴다.
b) 깃 허브 등록
- mattpocock의 to-issues 스킬을 사용하여 요구사항을 구현 기능 단위로 쪼개고 깃 허브 이슈로 등록한다.
 
**2. 개발 에이전트**
a) 하네스
- 카카오 개발자 revfactory의 하네스 에이전트를 사용하여 자동적으로 프로젝트의 하네스를 구축한다.
b) 개발
- 개발은 사용할 언어의 LSP를 사용하여 밀도 높은 코드로 작성한다.
- 기능 구현 시 mattpocock의 hand-off 스킬을 사용하여 인수인계 문서 작성. 새로운 세션에서 작업 시 자동으로 이를 읽는다.
c) 코드 개선
- mattpocock의 improve-codebase-architacture 스킬을 사용하여 코드를 리팩토링 한다.

### 에이전트 간 데이터 전달

에이전트끼리 직접 통신하지 않고 `_workspace/` 파일을 경유:

```
backend-dev  →  issue{N}_api_contract.md  →  frontend-dev
                     ↑
             엔드포인트 URL, 요청/응답 스키마 명세
```

재시작해도 `_workspace/` 파일 존재 여부로 진행 단계 자동 감지 → 완료된 단계 스킵.

---

## 개발 방법론

- **TDD** — pytest + httpx로 테스트 먼저 작성 후 구현. 55개 테스트 통과.
- **승인 워크플로우** — 기업 프로필이 관리자 승인 전까지 공개 목록에서 제외되어 신뢰성 확보.
- **JWT Refresh 전략** — Access Token 단기 만료 + Refresh Token 장기 유지로 보안·UX 균형.
- **이미지 서빙** — UUID 파일명 + FastAPI StaticFiles. 추후 S3/Cloudinary 교체 시 URL만 변경.

---
