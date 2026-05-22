# Company Discovery Platform

기업 소개 플랫폼. 기업 프로필 등록 + AI 챗봇 검색.

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Nuxt.js 3 + Tailwind CSS |
| Backend | FastAPI (Python) |
| DB | PostgreSQL 16 (Docker) |
| AI | Ollama llama3.1:8b + RAG |

## 로컬 개발 환경 실행

### 사전 요구사항

- Docker Desktop
- Python 3.11+
- Node.js 20+
- Ollama (`ollama pull llama3.1:8b`)

### 1. DB 실행

```bash
docker-compose up -d
```

### 2. 백엔드 실행

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env         # 환경변수 설정
alembic upgrade head         # DB 마이그레이션
uvicorn app.main:app --reload
```

API: http://localhost:8000
Docs: http://localhost:8000/docs

### 3. 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:3000

### 4. AI 챗봇 (Ollama)

```bash
ollama serve
ollama pull llama3.1:8b
```
