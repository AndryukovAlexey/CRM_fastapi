import pytest
from httpx import AsyncClient, ASGITransport
import aioredis
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import settings
from main import app
from models import Base


test_engine = create_async_engine(settings.DATABASE_URL_TEST)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)

# если бд голая
# @pytest.fixture(scope="module", autouse=True)
# async def init_test_db():
#     async with test_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)  # Создаём таблицы

@pytest.fixture(scope="function")
async def async_client():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
        yield client

@pytest.fixture(scope="function")
async def mock_redis():
    redis_mock = AsyncMock(spec=aioredis.Redis)
    redis_mock.get = AsyncMock(return_value=None)  # Симулируем отсутствие кэша
    redis_mock.set = AsyncMock(return_value=None)
    redis_mock.delete = AsyncMock(return_value=None)
    return redis_mock

