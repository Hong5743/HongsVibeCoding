from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.api.company import router as company_router

app = FastAPI(title="Company Discovery Platform API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


app.include_router(auth_router, prefix="/api")
app.include_router(company_router, prefix="/api")
app.include_router(admin_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
