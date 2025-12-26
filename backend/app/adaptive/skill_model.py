from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SkillEvent:
    skill_id: str
    quality: int  # 0..5
    ts: datetime
