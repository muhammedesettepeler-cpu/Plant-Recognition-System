from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List
import os
from pathlib import Path

# Find .env file - works from any directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=str(ENV_FILE),
        case_sensitive=True
    )
    PROJECT_NAME: str = "Plant Recognition System"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS - Frontend URL'leri
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
    
    @property
    def get_allowed_origins(self) -> List[str]:
        """ALLOWED_ORIGINS'i liste olarak döndür"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # Database
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "plant_recognition")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # APIs
    WEAVIATE_URL: str = os.getenv("WEAVIATE_URL", "http://localhost:8080")
    WEAVIATE_API_KEY: str = os.getenv("WEAVIATE_API_KEY", "")
    WEAVIATE_GRPC_HOST: str = os.getenv("WEAVIATE_GRPC_HOST", "")
    GROK_API_KEY: str = os.getenv("GROK_API_KEY", "")
    GROK_API_URL: str = os.getenv("GROK_API_URL", "https://api.x.ai/v1")
    PLANTNET_API_KEY: str = os.getenv("PLANTNET_API_KEY", "")
    PLANTNET_API_URL: str = "https://my-api.plantnet.org/v2/identify/all"
    
    # OpenRouter (Grok alternatifi - ücretsiz ve güçlü!)
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-nano-9b-v2:free")

    # Google AI Studio (optional) - prefer this if API key provided
    GOOGLE_AI_STUDIO_API_KEY: str = os.getenv("GOOGLE_AI_STUDIO_API_KEY", "")
    GOOGLE_AI_STUDIO_BASE_URL: str = os.getenv("GOOGLE_AI_STUDIO_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
    GOOGLE_AI_STUDIO_MODEL: str = os.getenv("GOOGLE_AI_STUDIO_MODEL", "gemini-2.0-flash-exp")
    
    # Redis (Optional - for production)
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    
    @property
    def REDIS_ENABLED(self) -> bool:
        """Check if Redis is enabled and accessible"""
        return bool(self.REDIS_URL)
    
    # Settings
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/jpg"]
    CLIP_MODEL_NAME: str = "openai/clip-vit-base-patch32"
    SIMILARITY_THRESHOLD: float = 0.7
    TOP_K_RESULTS: int = 5
    
    # Security settings
    REQUIRE_API_KEY: bool = os.getenv("REQUIRE_API_KEY", "false").lower() == "true"
    VALID_API_KEYS: str = os.getenv("VALID_API_KEYS", "")
    MAX_IMAGE_SIZE_MB: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    ENABLE_IMAGE_SANITIZATION: bool = os.getenv("ENABLE_IMAGE_SANITIZATION", "true").lower() == "true"

settings = Settings()
