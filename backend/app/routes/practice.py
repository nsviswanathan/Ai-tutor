from __future__ import annotations

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas import PracticeNextRequest, PracticePlan, SkillOut
from ..db.session import make_sessionmaker
from ..db.models import Skill
from ..adaptive.scheduler import score_candidate
from ..context.scenarios import pick_scenario

router = APIRouter(prefix="/api", tags=["practice"])

_engine, SessionLocal = make_sessionmaker()


async def get_db():
    async with SessionLocal() as session:
        yield session


def as_utc(dt: datetime | None) -> datetime | None:
    """
    Normalize datetimes for safe comparisons.

    SQLite often returns timezone-naive datetimes even if timezone=True.
    We treat naive datetimes as UTC to keep ordering consistent.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@router.post("/practice/next", response_model=PracticePlan)
async def practice_next(req: PracticeNextRequest, db: AsyncSession = Depends(get_db)):
    # fetch all skills for user
    skills = (await db.execute(select(Skill).where(Skill.user_id == req.user_id))).scalars().all()

    now = datetime.now(tz=timezone.utc)

    # rank candidates
    candidates = []
    for s in skills:
        next_due = as_utc(s.next_due)
        due = (next_due is None) or (next_due <= now)
        sc = score_candidate(due=due, strength=s.strength, next_due=next_due)
        candidates.append((sc, due, s, next_due))

    candidates.sort(key=lambda x: x[0])

    due_list = []
    weak_list = []

    # pick due first, then weak
    for _, due, s, next_due in candidates[: max(req.limit, 10)]:
        out = SkillOut(
            skill_id=s.skill_id,
            strength=s.strength,
            next_due=next_due,  # normalized
            streak=s.streak,
            mistakes=s.mistakes,
        )
        if due and len(due_list) < req.limit:
            due_list.append(out)
        elif (not due) and len(weak_list) < max(0, req.limit - len(due_list)):
            weak_list.append(out)

    # Suggest a few new skills based on context
    new_map = {
        "Airport": ["phrase:check_in", "vocab:overweight_bag", "phrase:rebook_flight"],
        "Restaurant": ["phrase:table_for_two", "vocab:allergy", "phrase:order_modification"],
        "Classroom": ["phrase:ask_clarification", "phrase:request_extension", "vocab:assignment"],
        "Office": ["phrase:status_update", "phrase:disagree_politely", "phrase:schedule_meeting"],
        "Shopping": ["phrase:return_item", "vocab:refund", "phrase:ask_alternative"],
    }
    suggested = new_map.get(req.context, new_map["Airport"])
    existing = {s.skill_id for s in skills}
    new_skills = [x for x in suggested if x not in existing][:3]

    scenario = pick_scenario(req.context)

    return PracticePlan(
        due=due_list,
        weak=weak_list,
        new=new_skills,
        scenario_prompt=scenario,
    )