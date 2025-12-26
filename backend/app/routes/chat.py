from __future__ import annotations
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas import ChatRequest, ChatResponse, SkillUpdate
from ..db.session import make_sessionmaker
from ..db.models import Skill, ChatTurn, ActivityLog
from ..adaptive.scheduler import SkillState, update_skill
from ..tutor.chat import call_llm

router = APIRouter(prefix="/api", tags=["chat"])

_engine, SessionLocal = make_sessionmaker()

async def get_db():
    async with SessionLocal() as session:
        yield session

def to_state(s: Skill) -> SkillState:
    return SkillState(
        strength=s.strength,
        ease=s.ease,
        interval_days=s.interval_days,
        last_seen=s.last_seen,
        next_due=s.next_due,
        streak=s.streak,
        mistakes=s.mistakes,
    )

def apply_state(s: Skill, st: SkillState):
    s.strength = st.strength
    s.ease = st.ease
    s.interval_days = st.interval_days
    s.last_seen = st.last_seen
    s.next_due = st.next_due
    s.streak = st.streak
    s.mistakes = st.mistakes

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    # Save user message
    t = datetime.now(tz=timezone.utc)
    db.add(ChatTurn(user_id=req.user_id, role="user", content=req.message, ts=t))
    # Log activity: count this turn as 1 minute by default (simple heuristic)
    db.add(ActivityLog(user_id=req.user_id, context=req.context, minutes=1, turns=1, ts=t))
    await db.commit()

    # Pull last few turns (server-side) to maintain continuity
    q = select(ChatTurn).where(ChatTurn.user_id == req.user_id).order_by(ChatTurn.id.desc()).limit(12)
    turns = list(reversed((await db.execute(q)).scalars().all()))
    history = [{"role": x.role, "content": x.content} for x in turns if x.role in ("user","assistant")]

    llm = await call_llm(req.context, req.level, req.message, history=history[:-1])  # exclude current user msg already added
    reply = llm["reply"]
    extracted = [SkillUpdate(**s) for s in llm.get("skills", []) if "skill_id" in s and "quality" in s]

    # Save assistant reply
    db.add(ChatTurn(user_id=req.user_id, role="assistant", content=reply, ts=datetime.now(tz=timezone.utc)))

    # Upsert/update skills based on extracted data
    for su in extracted:
        row = (await db.execute(
            select(Skill).where(Skill.user_id == req.user_id, Skill.skill_id == su.skill_id)
        )).scalars().first()
        if row is None:
            row = Skill(user_id=req.user_id, skill_id=su.skill_id)
            db.add(row)
            await db.flush()

        st = update_skill(to_state(row), quality=su.quality)
        apply_state(row, st)

    await db.commit()
    return ChatResponse(reply=reply, extracted_skills=extracted, turn_logged=True)
