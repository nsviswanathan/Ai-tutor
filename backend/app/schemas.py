from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict

class ChatRequest(BaseModel):
    user_id: str = "demo"
    context: str = "Airport"
    level: str = "Beginner"
    message: str
    history: List[Dict[str, str]] = Field(default_factory=list)

class SkillUpdate(BaseModel):
    skill_id: str
    quality: int = Field(ge=0, le=5)

class ChatResponse(BaseModel):
    reply: str
    extracted_skills: List[SkillUpdate] = Field(default_factory=list)
    # simple signal for the UI to track progress
    turn_logged: bool = True

class PracticeNextRequest(BaseModel):
    user_id: str = "demo"
    context: str = "Airport"
    level: str = "Beginner"
    limit: int = Field(default=6, ge=1, le=20)

class SkillOut(BaseModel):
    skill_id: str
    strength: float
    next_due: Optional[datetime]
    streak: int
    mistakes: int

class PracticePlan(BaseModel):
    due: List[SkillOut] = Field(default_factory=list)
    weak: List[SkillOut] = Field(default_factory=list)
    new: List[str] = Field(default_factory=list)
    scenario_prompt: str

class ProfileIn(BaseModel):
    user_id: str = "demo"
    native_language: str = "English"
    target_language: str = "English"
    level: str = "Beginner"
    daily_minutes_goal: int = Field(default=10, ge=1, le=240)
    weekly_minutes_goal: int = Field(default=70, ge=1, le=2000)
    focus_contexts: List[str] = Field(default_factory=lambda: ["Airport", "Restaurant"])

class ProfileOut(ProfileIn):
    created_at: datetime
    updated_at: datetime

class LogActivityIn(BaseModel):
    user_id: str = "demo"
    context: str = "Airport"
    minutes: int = Field(default=1, ge=0, le=480)
    turns: int = Field(default=1, ge=0, le=500)

class ProgressOut(BaseModel):
    user_id: str
    today_minutes: int
    week_minutes: int
    daily_goal: int
    weekly_goal: int
    daily_pct: float
    weekly_pct: float
    last_activity: Optional[datetime] = None
