from __future__ import annotations
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .models import Base

def get_engine():
    url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/app.db")
    return create_async_engine(url, echo=False)

async def init_db():
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
