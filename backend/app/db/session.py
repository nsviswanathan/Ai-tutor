from __future__ import annotations
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

def make_sessionmaker():
    url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/app.db")
    engine = create_async_engine(url, echo=False)
    return engine, async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
