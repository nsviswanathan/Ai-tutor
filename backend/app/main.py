from __future__ import annotations
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .db.init_db import init_db
from .routes.chat import router as chat_router
from .routes.practice import router as practice_router
from .routes.skills import router as skills_router
from .routes.session import router as session_router
from .routes.profile import router as profile_router

load_dotenv()

app = FastAPI(title="AI Tutor", version="0.1.0")

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(practice_router)
app.include_router(skills_router)
app.include_router(session_router)
app.include_router(profile_router)

@app.on_event("startup")
async def _startup():
    # ensure data dir exists for sqlite file
    os.makedirs("data", exist_ok=True)
    await init_db()

@app.get("/")
async def root():
    return {"ok": True, "service": "ai-tutor-backend"}
