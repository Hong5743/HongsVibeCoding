---
name: issue-dev
description: |
  vibecoding(기업 소개 플랫폼) 이슈 단위 풀스택 개발 오케스트레이터.
  이슈 번호와 기능 설명을 받아 백엔드(FastAPI TDD) → 프론트엔드(Nuxt.js) → 코드 리뷰 → 커밋 파이프라인을 자동 실행한다.

  트리거: "이슈 #N 진행해줘", "#N 구현", "다음 이슈 개발", "이슈 #N 작업 시작", "이슈 #N 이어서 해줘",
  "백엔드만 다시", "프론트엔드 재구현", "이슈 #N 완성해줘" 등 vibecoding GitHub 이슈 개발 요청 시 반드시 사용할 것.
---

# Issue Dev — 풀스택 개발 오케스트레이터

vibecoding 이슈 단위 개발을 **서브 에이전트 파이프라인**으로 처리한다.

## 실행 모드

**서브 에이전트** — 백엔드 → 프론트엔드 순차 실행, 파일 기반 데이터 전달.
팀 통신 없이 오케스트레이터가 각 에이전트를 직접 호출하고 결과를 수집한다.

## 데이터 전달

중간 산출물은 `_workspace/` 폴더에 저장 (커밋 제외):
- `_workspace/issue{N}_plan.md` — 분석 결과
- `_workspace/issue{N}_api_contract.md` — 백엔드 API 계약 (프론트엔드 입력)

---

## Phase 0: 컨텍스트 확인

1. 이슈 번호(N) 확인
2. `_workspace/issue{N}_api_contract.md` 존재 여부 확인:
   - 존재 → 백엔드 완료. 프론트엔드(Phase 3)부터 재개
   - 없음 → 초기 실행. Phase 1부터 전체 실행
3. `PRD.md` 읽기 (항상)
4. handoff 문서 있으면 참조: `C:/Users/ghd57/AppData/Local/Temp/handoff-vibecoding-*.md`

## Phase 1: 분석

`PRD.md`에서 해당 이슈 관련 항목 추출:
- User Stories (해당 번호)
- Implementation Decisions (API 설계, 스키마)
- 백엔드 엔드포인트 목록
- 프론트엔드 화면/컴포넌트 목록

결과를 `_workspace/issue{N}_plan.md`에 저장.

## Phase 2: 백엔드 구현

`backend-dev` 에이전트 호출:

```
Agent(
  description="이슈 #{N} 백엔드 TDD 구현",
  subagent_type="backend-dev",
  model="opus",
  prompt="""
  이슈 #{N} 백엔드 구현.

  계획서: D:\\홍민호\\사업\\vibecoding\\_workspace\\issue{N}_plan.md
  프로젝트: D:\\홍민호\\사업\\vibecoding\\backend

  1. tests/test_{모듈명}.py에 테스트 먼저 작성 (TDD)
  2. app/api/{모듈명}.py 구현
  3. app/main.py에 router 등록
  4. python -m pytest tests/ -v 전체 통과 확인
  5. _workspace/issue{N}_api_contract.md에 API 계약 저장
  """
)
```

실패 시 1회 재시도. 재실패 시 이슈 내용 조정 후 진행.

## Phase 3: 프론트엔드 구현

`frontend-dev` 에이전트 호출:

```
Agent(
  description="이슈 #{N} 프론트엔드 구현",
  subagent_type="frontend-dev",
  model="opus",
  prompt="""
  이슈 #{N} 프론트엔드 구현.

  API 계약: D:\\홍민호\\사업\\vibecoding\\_workspace\\issue{N}_api_contract.md
  프로젝트: D:\\홍민호\\사업\\vibecoding\\frontend

  1. 필요한 composable 추가/수정 (composables/)
  2. 페이지/컴포넌트 구현 (pages/ 또는 components/)
  3. 로딩/에러/빈 상태 처리 필수
  """
)
```

## Phase 4: 코드 리뷰

`code-reviewer` 에이전트 호출:

```
Agent(
  description="이슈 #{N} 코드 리뷰",
  subagent_type="code-reviewer",
  model="opus",
  prompt="""
  이슈 #{N} 변경 파일 리뷰.
  프로젝트: D:\\홍민호\\사업\\vibecoding

  git diff HEAD~1 으로 변경사항 확인.
  CRITICAL/HIGH/MEDIUM/LOW 심각도로 보고.
  승인 여부(APPROVED/WARN/BLOCKED) 포함.
  """
)
```

BLOCKED 판정 시:
- 백엔드 이슈 → backend-dev 재호출
- 프론트엔드 이슈 → frontend-dev 재호출
- 수정 후 리뷰 재실행

## Phase 5: 커밋

전체 테스트 통과 확인 후:
```
cd backend && python -m pytest tests/ -v
git add {변경파일들}
git commit -m "feat: #{N} {기능 설명}"
```

---

## 에러 핸들링

| 상황 | 처리 |
|------|------|
| 백엔드 테스트 실패 | backend-dev 1회 재호출 |
| CRITICAL 리뷰 이슈 | 해당 에이전트 재호출 후 리뷰 재실행 |
| Ollama 연동 오류 | `.env`의 `OLLAMA_BASE_URL` 확인 요청 |
| `_workspace/` 없음 | 디렉토리 생성 후 진행 |

## 테스트 시나리오

**정상 흐름 — "이슈 #8 AI Chat 진행해줘":**
1. Phase 0: `_workspace/issue8_api_contract.md` 없음 → 전체 실행
2. Phase 1: PRD에서 AI Chat 요구사항 추출
3. Phase 2: backend-dev → `POST /api/chat` TDD 구현
4. Phase 3: frontend-dev → `ChatBot.vue` 구현
5. Phase 4: code-reviewer → APPROVED
6. Phase 5: `feat: #8 AI chat with Ollama RAG` 커밋

**재개 흐름 — "이슈 #8 프론트엔드만 다시 해줘":**
1. Phase 0: `_workspace/issue8_api_contract.md` 존재 → Phase 3부터
2. Phase 3: frontend-dev 재호출
3. Phase 4~5 정상 진행
