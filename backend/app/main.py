from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, auth, chat, patients, stats, studies
from app.config import get_settings
from app.database import SessionLocal, init_db
from app.seed import seed

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    with SessionLocal() as db:
        seed(db)
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Backend for AI-LLM Based Medical Imaging Classification and Segmentation "
    "(brain MRI) with role-based access: admin, doctor, radiologist, patient.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (auth.router, admin.router, patients.router, studies.router, stats.router, chat.router):
    app.include_router(r)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok", "llmProvider": settings.llm_provider}
