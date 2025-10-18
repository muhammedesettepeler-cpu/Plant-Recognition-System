"""
Redis Usage Examples - Cache & Rate Limiting
"""
from app.services.redis_service import redis_service
from app.core.rate_limiter import rate_limiter, strict_rate_limiter
from fastapi import APIRouter, Depends, Request
import hashlib

router = APIRouter()

# Example 1: Simple caching
@router.get("/plants/{plant_id}")
async def get_plant(plant_id: str):
    """Get plant info with caching"""
    
    # Try cache first
    cache_key = f"plant:{plant_id}"
    cached = await redis_service.get_json(cache_key)
    if cached:
        return {"source": "cache", "data": cached}
    
    # Fetch from database (simulated)
    plant_data = {
        "id": plant_id,
        "name": "Rosa gallica",
        "family": "Rosaceae"
    }
    
    # Cache for 1 hour
    await redis_service.set_json(cache_key, plant_data, expire=3600)
    
    return {"source": "database", "data": plant_data}


# Example 2: Image similarity cache
async def get_cached_similarity(image_bytes: bytes):
    """Cache similarity search results"""
    
    # Generate cache key from image hash
    image_hash = hashlib.sha256(image_bytes).hexdigest()[:16]
    cache_key = f"similarity:{image_hash}"
    
    # Check cache
    cached = await redis_service.get_json(cache_key)
    if cached:
        return cached
    
    # Compute similarity (expensive operation)
    from app.services.clip_service import clip_service
    from app.services.weaviate_service import weaviate_service
    
    embedding = clip_service.encode_image(image_bytes)
    results = weaviate_service.similarity_search(embedding)
    
    # Cache for 24 hours
    await redis_service.set_json(cache_key, results, expire=86400)
    
    return results


# Example 3: Rate limiting
@router.post("/expensive-operation", dependencies=[Depends(strict_rate_limiter)])
async def expensive_operation(request: Request):
    """
    Expensive operation with strict rate limiting (5/min)
    Redis automatically tracks this across multiple servers
    """
    return {"message": "Operation completed"}


@router.post("/normal-operation", dependencies=[Depends(rate_limiter)])
async def normal_operation(request: Request):
    """
    Normal operation with standard rate limiting (10/min)
    """
    return {"message": "Operation completed"}


# Example 4: Manual rate limit check
@router.post("/custom-rate-limit")
async def custom_rate_limit(request: Request):
    """Custom rate limit logic"""
    
    # Check manually
    allowed = await rate_limiter.check_rate_limit(request)
    if not allowed:
        return {"error": "Too many requests"}, 429
    
    # Process request
    return {"message": "Success"}


# Example 5: LLM response caching
async def get_llm_response_cached(prompt: str, plant_context: str):
    """Cache LLM responses to save API calls"""
    
    # Generate cache key
    cache_key = f"llm:{hashlib.sha256(f'{prompt}:{plant_context}'.encode()).hexdigest()[:16]}"
    
    # Check cache
    cached = await redis_service.get(cache_key)
    if cached:
        return {"source": "cache", "response": cached}
    
    # Generate response (expensive)
    from app.services.llm_service import llm_service
    response = await llm_service.generate_response(prompt, plant_context)
    
    # Cache for 7 days
    await redis_service.set(cache_key, response, expire=604800)
    
    return {"source": "llm", "response": response}
