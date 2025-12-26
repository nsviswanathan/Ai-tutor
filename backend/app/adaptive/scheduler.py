from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

UTC = timezone.utc

@dataclass
class SkillState:
    strength: float  # 0..1
    ease: float      # ~1.3..2.7
    interval_days: int
    last_seen: datetime | None
    next_due: datetime | None
    streak: int
    mistakes: int

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def now_utc() -> datetime:
    return datetime.now(tz=UTC)

def update_skill(state: SkillState, quality: int) -> SkillState:
    """Update scheduling based on a 0..5 quality score.
    - quality 0-2: failure (schedule soon, reduce strength)
    - quality 3-5: success (increase interval, boost strength)
    """
    t = now_utc()
    # Normalize quality
    q = clamp(float(quality), 0.0, 5.0)

    # Mistake vs success
    if q < 3.0:
        state.mistakes += 1
        state.streak = 0
        state.strength = clamp(state.strength - 0.15, 0.0, 1.0)
        state.ease = clamp(state.ease - 0.15, 1.3, 2.7)
        state.interval_days = 1
        state.next_due = t + timedelta(hours=8)  # quick retry
    else:
        state.streak += 1
        # Ease factor update (SM-2-like)
        state.ease = clamp(state.ease + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)), 1.3, 2.7)
        # Interval growth
        if state.interval_days <= 1:
            state.interval_days = 2
        else:
            state.interval_days = int(round(state.interval_days * state.ease))
        # Strength grows slower as you approach 1.0
        gain = 0.08 + 0.02 * (q - 3.0)
        state.strength = clamp(state.strength + gain * (1.0 - state.strength), 0.0, 1.0)
        state.next_due = t + timedelta(days=state.interval_days)

    state.last_seen = t
    return state

def score_candidate(due: bool, strength: float, next_due: datetime | None) -> float:
    """Lower score => higher priority."""
    base = 1.0 - strength
    if due:
        return base - 0.5
    if next_due:
        # time until due in hours
        dt = (next_due - now_utc()).total_seconds() / 3600.0
        # soon-due gets better score
        return base + clamp(dt / 72.0, 0.0, 2.0)
    return base + 2.0
