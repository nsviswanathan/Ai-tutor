from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import make_sessionmaker
from ..db.models import Skill

router = APIRouter(prefix="/api", tags=["skills"])

_engine, SessionLocal = make_sessionmaker()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/skills/{user_id}")
async def list_skills(user_id: str, db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(Skill).where(Skill.user_id == user_id).order_by(Skill.next_due.asc().nullsfirst()))).scalars().all()
    return [
        {
            "skill_id": r.skill_id,
            "strength": r.strength,
            "ease": r.ease,
            "interval_days": r.interval_days,
            "last_seen": r.last_seen,
            "next_due": r.next_due,
            "streak": r.streak,
            "mistakes": r.mistakes,
        }
        for r in rows
    ]
