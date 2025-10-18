from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.core.config import settings
from app.api import plant_recognition, chatbot, health
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="LLM-Supported Intelligent Plant Recognition System",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

@app.on_event("startup")
async def startup_event():
    """
    Load models and establish connections on startup
    This prevents cold-start delays on first request
    """
    logger.info("Starting application initialization...")
    
    # Connect to Redis (optional - for caching and rate limiting)
    try:
        from app.services.redis_service import redis_service
        logger.info("Connecting to Redis...")
        await redis_service.connect()
        if redis_service.is_connected:
            logger.info("✅ Redis connected - using distributed cache")
        else:
            logger.info("⚠️  Redis not available - using in-memory fallback")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e} - using in-memory fallback")
    
    # Load CLIP model
    try:
        from app.services.clip_service import clip_service
        logger.info("Loading CLIP model...")
        clip_service.load_model()
        logger.info("CLIP model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load CLIP model: {e}")
    
    # Connect to Weaviate
    try:
        from app.services.weaviate_service import weaviate_service
        logger.info("Connecting to Weaviate Cloud...")
        weaviate_service.connect()
        logger.info("Weaviate connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Weaviate: {e}")
    
    logger.info("Application initialization completed")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application...")
    
    # Disconnect Redis
    try:
        from app.services.redis_service import redis_service
        await redis_service.disconnect()
    except Exception as e:
        logger.error(f"Redis disconnect error: {e}")

# CORS Middleware - Frontend'in API'ye erişmesini sağlar
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# GZip Middleware - Response'ları sıkıştırır
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routers
app.include_router(health.router, prefix=settings.API_V1_PREFIX, tags=["health"])
app.include_router(plant_recognition.router, prefix=settings.API_V1_PREFIX, tags=["recognition"])
app.include_router(chatbot.router, prefix=settings.API_V1_PREFIX, tags=["chatbot"])

@app.get("/")
async def root():
    return {
        "message": "Plant Recognition System API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs"
    }
