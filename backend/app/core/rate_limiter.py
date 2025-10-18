"""
Advanced rate limiting with Redis support
Falls back to in-memory if Redis unavailable
"""
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
from typing import Dict, Optional
import hashlib
from app.services.redis_service import redis_service
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Rate limiter with Redis support
    Falls back to in-memory if Redis unavailable
    """
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        # In-memory fallback
        self._memory_cache: Dict[str, list] = {}
    
    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier"""
        # Try to get user ID from request state (if authenticated)
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"
        
        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        return f"ip:{ip}"
    
    def _get_cache_key(self, client_id: str) -> str:
        """Generate Redis cache key"""
        return f"rate_limit:{client_id}"
    
    async def _check_redis(self, client_id: str) -> bool:
        """Check rate limit using Redis"""
        key = self._get_cache_key(client_id)
        
        # Increment counter
        count = await redis_service.increment(key, expire=60)
        
        if count > self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_id}: {count}/{self.requests_per_minute}")
            return False
        
        logger.debug(f"Rate limit OK for {client_id}: {count}/{self.requests_per_minute}")
        return True
    
    def _check_memory(self, client_id: str) -> bool:
        """Check rate limit using in-memory cache (fallback)"""
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        
        # Clean old entries
        if client_id in self._memory_cache:
            self._memory_cache[client_id] = [
                ts for ts in self._memory_cache[client_id]
                if ts > cutoff
            ]
        else:
            self._memory_cache[client_id] = []
        
        # Check limit
        if len(self._memory_cache[client_id]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded (memory) for {client_id}")
            return False
        
        # Add current request
        self._memory_cache[client_id].append(now)
        return True
    
    async def check_rate_limit(self, request: Request) -> bool:
        """
        Check if request is within rate limit
        Returns True if allowed, False if rate limited
        """
        client_id = self._get_client_id(request)
        
        # Try Redis first
        if redis_service.is_connected:
            return await self._check_redis(client_id)
        
        # Fall back to in-memory
        logger.debug("Using in-memory rate limiting (Redis not available)")
        return self._check_memory(client_id)
    
    async def __call__(self, request: Request):
        """
        FastAPI dependency for rate limiting
        Raises HTTPException if rate limit exceeded
        """
        allowed = await self.check_rate_limit(request)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.requests_per_minute} requests per minute allowed",
                    "retry_after": "60 seconds"
                }
            )

# Global instances
rate_limiter = RateLimiter(requests_per_minute=10)
strict_rate_limiter = RateLimiter(requests_per_minute=5)  # For expensive operations
