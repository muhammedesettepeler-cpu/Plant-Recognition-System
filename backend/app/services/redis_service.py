"""
Redis service for caching and rate limiting
"""
from typing import Optional
import redis.asyncio as redis
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self._connected = False
    
    async def connect(self):
        """Connect to Redis"""
        if not settings.REDIS_ENABLED:
            logger.info("Redis not enabled - using in-memory fallback")
            return
        
        try:
            self.client = redis.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            # Test connection
            await self.client.ping()
            self._connected = True
            logger.info("✅ Redis connected successfully")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self._connected = False
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
            self._connected = False
            logger.info("Redis disconnected")
    
    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        return self._connected and self.client is not None
    
    # Cache operations
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if not self.is_connected:
            return None
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None
    
    async def set(self, key: str, value: str, expire: int = 3600):
        """Set value in cache with TTL"""
        if not self.is_connected:
            return False
        try:
            await self.client.set(key, value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False
    
    async def get_json(self, key: str) -> Optional[dict]:
        """Get JSON value from cache"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    async def set_json(self, key: str, value: dict, expire: int = 3600):
        """Set JSON value in cache"""
        try:
            json_str = json.dumps(value)
            return await self.set(key, json_str, expire)
        except Exception as e:
            logger.error(f"Redis SET JSON error: {e}")
            return False
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.is_connected:
            return False
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False
    
    # Rate limiting operations
    async def increment(self, key: str, expire: int = 60) -> int:
        """Increment counter (for rate limiting)"""
        if not self.is_connected:
            return 0
        try:
            pipe = self.client.pipeline()
            pipe.incr(key)
            pipe.expire(key, expire)
            results = await pipe.execute()
            return results[0]  # Return count
        except Exception as e:
            logger.error(f"Redis INCR error: {e}")
            return 0
    
    async def get_count(self, key: str) -> int:
        """Get counter value"""
        if not self.is_connected:
            return 0
        try:
            value = await self.client.get(key)
            return int(value) if value else 0
        except Exception as e:
            logger.error(f"Redis GET COUNT error: {e}")
            return 0

# Global instance
redis_service = RedisService()
