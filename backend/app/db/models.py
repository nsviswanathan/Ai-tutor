from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Float, DateTime, Text, Boolean

class Base(DeclarativeBase):
    pass

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, unique=True, index=True)

    native_language: Mapped[str] = mapped_column(String, default="English")
    target_language: Mapped[str] = mapped_column(String, default="English")
    level: Mapped[str] = mapped_column(String, default="Beginner")

    # Goal settings
    daily_minutes_goal: Mapped[int] = mapped_column(Integer, default=10)
    weekly_minutes_goal: Mapped[int] = mapped_column(Integer, default=70)
    focus_contexts: Mapped[str] = mapped_column(String, default="Airport,Restaurant")  # comma-separated

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    skill_id: Mapped[str] = mapped_column(String, index=True)

    strength: Mapped[float] = mapped_column(Float, default=0.3)
    ease: Mapped[float] = mapped_column(Float, default=2.0)
    interval_days: Mapped[int] = mapped_column(Integer, default=1)

    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_due: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    streak: Mapped[int] = mapped_column(Integer, default=0)
    mistakes: Mapped[int] = mapped_column(Integer, default=0)

class ChatTurn(Base):
    __tablename__ = "chat_turns"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    role: Mapped[str] = mapped_column(String)  # user/assistant
    content: Mapped[str] = mapped_column(Text)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    context: Mapped[str] = mapped_column(String, default="Unknown")
    minutes: Mapped[int] = mapped_column(Integer, default=0)
    turns: Mapped[int] = mapped_column(Integer, default=0)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
