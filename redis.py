import aioredis

from config import settings

redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True, encoding="utf-8")
