"""
Custom exception classes for Plant Recognition System
Provides structured error handling with clear, actionable error messages
"""
from fastapi import HTTPException, status


class PlantRecognitionException(Exception):
    """Base exception for all custom exceptions"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class WeaviateConnectionError(PlantRecognitionException):
    """Raised when Weaviate connection fails"""
    def __init__(self, message: str = "Failed to connect to Weaviate vector database", details: dict = None):
        super().__init__(message, details)


class CLIPModelError(PlantRecognitionException):
    """Raised when CLIP model operations fail"""
    def __init__(self, message: str = "CLIP model error", details: dict = None):
        super().__init__(message, details)


class PlantNetAPIError(PlantRecognitionException):
    """Raised when PlantNet API call fails"""
    def __init__(self, message: str = "PlantNet API request failed", details: dict = None):
        super().__init__(message, details)


class ImageValidationError(PlantRecognitionException):
    """Raised when image validation fails"""
    def __init__(self, message: str = "Image validation failed", details: dict = None):
        super().__init__(message, details)


class DatabaseError(PlantRecognitionException):
    """Raised when database operations fail"""
    def __init__(self, message: str = "Database operation failed", details: dict = None):
        super().__init__(message, details)


class LLMServiceError(PlantRecognitionException):
    """Raised when LLM service (OpenRouter) fails"""
    def __init__(self, message: str = "LLM service request failed", details: dict = None):
        super().__init__(message, details)


class RateLimitError(PlantRecognitionException):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str = "Rate limit exceeded", details: dict = None):
        super().__init__(message, details)


def exception_to_http(exc: PlantRecognitionException) -> HTTPException:
    """Convert custom exception to HTTPException with appropriate status code"""
    
    status_map = {
        ImageValidationError: status.HTTP_400_BAD_REQUEST,
        RateLimitError: status.HTTP_429_TOO_MANY_REQUESTS,
        PlantNetAPIError: status.HTTP_503_SERVICE_UNAVAILABLE,
        LLMServiceError: status.HTTP_503_SERVICE_UNAVAILABLE,
        WeaviateConnectionError: status.HTTP_503_SERVICE_UNAVAILABLE,
        CLIPModelError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    
    status_code = status_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return HTTPException(
        status_code=status_code,
        detail={
            "error": exc.message,
            "details": exc.details,
            "type": type(exc).__name__
        }
    )
