from __future__ import annotations
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import make_sessionmaker
from ..db.models import ChatTurn

router = APIRouter(prefix="/api", tags=["session"])

_engine, SessionLocal = make_sessionmaker()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/history/{user_id}")
async def get_history(user_id: str, limit: int = 30, db: AsyncSession = Depends(get_db)):
    q = select(ChatTurn).where(ChatTurn.user_id == user_id).order_by(ChatTurn.id.desc()).limit(limit)
    rows = (await db.execute(q)).scalars().all()
    rows = list(reversed(rows))
    return [{"role": r.role, "content": r.content, "ts": r.ts} for r in rows]

@router.post("/history/{user_id}/clear")
async def clear_history(user_id: str, db: AsyncSession = Depends(get_db)):
    # simple delete all
    await db.execute(select(ChatTurn).where(ChatTurn.user_id == user_id))  # warm up
    await db.execute(
        ChatTurn.__table__.delete().where(ChatTurn.user_id == user_id)
    )
    await db.commit()
    return {"ok": True}
