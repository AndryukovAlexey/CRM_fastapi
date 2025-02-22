from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import Depends
from typing import Annotated

from config import settings
from models import Base


if settings.TEST_MODE:
    engine = create_async_engine(
        url=settings.DATABASE_URL_TEST,
    )
else:
    engine = create_async_engine(
        url=settings.DATABASE_URL,
    )

new_session = async_sessionmaker(engine, expire_on_commit=False)

# async def get_session():
#     async with new_session() as session:
#         yield session

# SessionDep = Annotated[AsyncSession, Depends(get_session)]

async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
