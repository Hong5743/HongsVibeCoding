# vibecoding — 기업 소개 플랫폼

## 하네스: issue-dev

**목표:** 이슈 번호 단위로 FastAPI 백엔드 + Nuxt.js 프론트엔드를 자동 개발

**트리거:** "이슈 #N 진행", "이슈 #N 구현", "다음 이슈 개발", "#N 작업 시작" 등 vibecoding 이슈 개발 요청 시 `issue-dev` 스킬을 사용하라. 단순 질문이나 단일 파일 수정은 직접 응답 가능.

**에이전트:** `.claude/agents/backend-dev.md`, `frontend-dev.md`, `code-reviewer.md`

**변경 이력:**
| 날짜 | 변경 내용 | 대상 | 사유 |
|------|----------|------|------|
| 2026-05-28 | 초기 구성 | 전체 | vibecoding 이슈 #7 완료 후 하네스 구성 |

---

## 프로젝트 현황

- **완료 이슈:** #2~#7 (Auth, Company CRUD, Admin, Public 목록/검색)
- **다음 이슈:** #8 AI Chat (Ollama + RAG) — `POST /api/chat`, `ChatBot.vue`
- **테스트:** `backend/tests/` 55개 통과
- **PRD:** `PRD.md` 참조
