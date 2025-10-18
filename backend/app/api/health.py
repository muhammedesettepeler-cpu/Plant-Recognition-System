from fastapi import APIRouter, Depends
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.base import get_db
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Comprehensive health check for all system components
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": settings.VERSION,
        "services": {}
    }
    
    # Database check
    try:
        db.execute(text("SELECT 1"))
        health_status["services"]["database"] = {
            "status": "healthy",
            "type": "PostgreSQL"
        }
    except Exception as e:
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Weaviate check
    try:
        from app.services.weaviate_service import weaviate_service
        if weaviate_service.client and weaviate_service.client.is_ready():
            health_status["services"]["weaviate"] = {
                "status": "healthy",
                "type": "Cloud"
            }
        else:
            health_status["services"]["weaviate"] = {
                "status": "disconnected"
            }
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["weaviate"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # CLIP model check
    try:
        from app.services.clip_service import clip_service
        if clip_service.model is not None:
            health_status["services"]["clip_model"] = {
                "status": "loaded",
                "device": clip_service.device
            }
        else:
            health_status["services"]["clip_model"] = {
                "status": "not_loaded"
            }
    except Exception as e:
        health_status["services"]["clip_model"] = {
            "status": "error",
            "error": str(e)
        }
    
    # API Keys validation - return simple status string
    api_keys_valid = all([
        bool(settings.WEAVIATE_API_KEY),
        bool(settings.OPENROUTER_API_KEY),
        bool(settings.PLANTNET_API_KEY)
    ])
    
    health_status["services"]["api_keys"] = "healthy" if api_keys_valid else "missing_keys"
    
    # Kaggle Notebook check (optional service)
    try:
        from app.services.kaggle_notebook_service import kaggle_notebook_service
        if kaggle_notebook_service.notebook_url:
            # Try to check availability (with timeout)
            is_available = await kaggle_notebook_service.check_availability()
            health_status["services"]["kaggle_notebook"] = {
                "status": "available" if is_available else "unavailable",
                "url_configured": True,
                "note": "PlantCLEF 2025 dataset (10k+ species)"
            }
        else:
            health_status["services"]["kaggle_notebook"] = {
                "status": "not_configured",
                "url_configured": False,
                "note": "Optional service for extended plant database"
            }
    except Exception as e:
        health_status["services"]["kaggle_notebook"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Redis check (optional service)
    try:
        from app.services.redis_service import redis_service
        health_status["services"]["redis"] = {
            "status": "connected" if redis_service.is_connected else "disconnected",
            "enabled": redis_service.is_connected
        }
    except Exception as e:
        health_status["services"]["redis"] = {
            "status": "not_available",
            "error": str(e)
        }
    
    return health_status

@router.get("/status")
async def system_status():
    """Simple status endpoint for quick checks"""
    return {
        "status": "ok",
        "timestamp": datetime.now(UTC).isoformat()
    }
