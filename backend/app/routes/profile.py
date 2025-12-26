from __future__ import annotations
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas import ProfileIn, ProfileOut, LogActivityIn, ProgressOut
from ..db.session import make_sessionmaker
from ..db.models import UserProfile, ActivityLog

router = APIRouter(prefix="/api", tags=["profile"])

_engine, SessionLocal = make_sessionmaker()

async def get_db():
    async with SessionLocal() as session:
        yield session

def _utcnow():
    return datetime.now(tz=timezone.utc)

@router.get("/profile/{user_id}", response_model=ProfileOut)
async def get_profile(user_id: str, db: AsyncSession = Depends(get_db)):
    row = (await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))).scalars().first()
    if row is None:
        now = _utcnow()
        row = UserProfile(
            user_id=user_id,
            native_language="English",
            target_language="English",
            level="Beginner",
            daily_minutes_goal=10,
            weekly_minutes_goal=70,
            focus_contexts="Airport,Restaurant",
            created_at=now,
            updated_at=now,
        )
        db.add(row)
        await db.commit()
        await db.refresh(row)

    return ProfileOut(
        user_id=row.user_id,
        native_language=row.native_language,
        target_language=row.target_language,
        level=row.level,
        daily_minutes_goal=row.daily_minutes_goal,
        weekly_minutes_goal=row.weekly_minutes_goal,
        focus_contexts=[c.strip() for c in (row.focus_contexts or "").split(",") if c.strip()],
        created_at=row.created_at,
        updated_at=row.updated_at,
    )

@router.put("/profile/{user_id}", response_model=ProfileOut)
async def upsert_profile(user_id: str, body: ProfileIn, db: AsyncSession = Depends(get_db)):
    now = _utcnow()
    row = (await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))).scalars().first()
    if row is None:
        row = UserProfile(
            user_id=user_id,
            created_at=now,
            updated_at=now,
        )
        db.add(row)
        await db.flush()

    row.native_language = body.native_language
    row.target_language = body.target_language
    row.level = body.level
    row.daily_minutes_goal = body.daily_minutes_goal
    row.weekly_minutes_goal = body.weekly_minutes_goal
    row.focus_contexts = ",".join(body.focus_contexts)
    row.updated_at = now

    await db.commit()
    await db.refresh(row)
    return await get_profile(user_id, db)

@router.post("/activity/log")
async def log_activity(body: LogActivityIn, db: AsyncSession = Depends(get_db)):
    db.add(ActivityLog(
        user_id=body.user_id,
        context=body.context,
        minutes=body.minutes,
        turns=body.turns,
        ts=_utcnow(),
    ))
    await db.commit()
    return {"ok": True}

@router.get("/progress/{user_id}", response_model=ProgressOut)
async def get_progress(user_id: str, db: AsyncSession = Depends(get_db)):
    profile = await get_profile(user_id, db)
    now = _utcnow()
    # Start of today (UTC) and start of week (last 7 days)
    start_today = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    start_week = start_today - timedelta(days=6)

    today_minutes = (await db.execute(
        select(func.coalesce(func.sum(ActivityLog.minutes), 0))
        .where(ActivityLog.user_id == user_id, ActivityLog.ts >= start_today)
    )).scalar_one()

    week_minutes = (await db.execute(
        select(func.coalesce(func.sum(ActivityLog.minutes), 0))
        .where(ActivityLog.user_id == user_id, ActivityLog.ts >= start_week)
    )).scalar_one()

    last_ts = (await db.execute(
        select(func.max(ActivityLog.ts)).where(ActivityLog.user_id == user_id)
    )).scalar_one()

    daily_pct = min(1.0, (today_minutes / profile.daily_minutes_goal) if profile.daily_minutes_goal else 0.0)
    weekly_pct = min(1.0, (week_minutes / profile.weekly_minutes_goal) if profile.weekly_minutes_goal else 0.0)

    return ProgressOut(
        user_id=user_id,
        today_minutes=int(today_minutes),
        week_minutes=int(week_minutes),
        daily_goal=profile.daily_minutes_goal,
        weekly_goal=profile.weekly_minutes_goal,
        daily_pct=float(daily_pct),
        weekly_pct=float(weekly_pct),
        last_activity=last_ts,
    )
