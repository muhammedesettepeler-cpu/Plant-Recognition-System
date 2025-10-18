"""
Security utilities for image upload and processing
"""
from fastapi import HTTPException, UploadFile, Header
from PIL import Image
import io
import hashlib
import secrets
from typing import Tuple, Optional
from app.core.config import settings
from app.core.exceptions import ImageValidationError, RateLimitError

class ImageSecurity:
    """Security checks for uploaded images"""
    
    # Allowed MIME types
    ALLOWED_MIME_TYPES = [
        "image/jpeg",
        "image/jpg", 
        "image/png",
        "image/webp"
    ]
    
    # Magic bytes for file type verification
    MAGIC_BYTES = {
        b'\xff\xd8\xff': 'image/jpeg',
        b'\x89PNG\r\n\x1a\n': 'image/png',
        b'RIFF': 'image/webp'
    }
    
    @staticmethod
    async def validate_image(
        file: UploadFile,
        max_size_mb: int = 10
    ) -> Tuple[bool, str, bytes]:
        """
        Comprehensive image validation:
        1. Size check
        2. MIME type verification
        3. Magic bytes validation
        4. PIL verification (exploit detection)
        5. Content sanitization
        
        Returns: (is_valid, error_message, sanitized_bytes)
        """
        try:
            # 1. Read file content
            content = await file.read()
            size_mb = len(content) / (1024 * 1024)
            
            # 2. Size validation
            if size_mb > max_size_mb:
                raise HTTPException(
                    status_code=413,
                    detail=f"Image too large: {size_mb:.2f}MB (max {max_size_mb}MB)"
                )
            
            # 3. MIME type check
            if file.content_type not in ImageSecurity.ALLOWED_MIME_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type: {file.content_type}. Allowed: {ImageSecurity.ALLOWED_MIME_TYPES}"
                )
            
            # 4. Magic bytes validation (prevent MIME spoofing)
            is_valid_magic = False
            for magic, mime in ImageSecurity.MAGIC_BYTES.items():
                if content.startswith(magic):
                    is_valid_magic = True
                    break
            
            if not is_valid_magic:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid image file: magic bytes don't match declared MIME type"
                )
            
            # 5. PIL verification (detect exploits/corrupted files)
            try:
                img = Image.open(io.BytesIO(content))
                img.verify()  # Verify it's a valid image
                
                # Re-open for actual processing (verify() closes file)
                img = Image.open(io.BytesIO(content))
                
                # 6. Content sanitization: re-encode to remove metadata/EXIF
                sanitized_buffer = io.BytesIO()
                img_format = img.format or 'JPEG'
                
                # Convert to RGB if needed (removes alpha channel)
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # Save without metadata
                img.save(sanitized_buffer, format=img_format, quality=95, optimize=True)
                sanitized_bytes = sanitized_buffer.getvalue()
                
                # 7. Size limits on dimensions
                if img.width > 4096 or img.height > 4096:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Image dimensions too large: {img.width}x{img.height} (max 4096x4096)"
                    )
                
                return True, "Valid", sanitized_bytes
                
            except Exception as pil_error:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid or corrupted image: {str(pil_error)}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Image validation error: {str(e)}"
            )
    
    @staticmethod
    def generate_safe_filename(original_filename: str) -> str:
        """
        Generate cryptographically secure random filename
        Prevents directory traversal and collision attacks
        """
        # Extract extension
        ext = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else 'jpg'
        
        # Generate random name
        random_name = secrets.token_hex(16)  # 32 chars
        
        return f"{random_name}.{ext}"
    
    @staticmethod
    def compute_image_hash(image_bytes: bytes) -> str:
        """
        Compute SHA256 hash for duplicate detection
        """
        return hashlib.sha256(image_bytes).hexdigest()


class AuthSecurity:
    """Authentication and authorization utilities"""
    
    @staticmethod
    async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
        """
        Verify API key for rate limiting and authentication
        In production: use JWT tokens or OAuth2
        """
        # For development: optional API key
        if not settings.REQUIRE_API_KEY:
            return True
        
        if not x_api_key:
            raise HTTPException(
                status_code=401,
                detail="Missing API key. Include X-API-Key header."
            )
        
        # In production: check against database/Redis
        valid_keys = settings.VALID_API_KEYS.split(',') if settings.VALID_API_KEYS else []
        
        if x_api_key not in valid_keys:
            raise HTTPException(
                status_code=403,
                detail="Invalid API key"
            )
        
        return True
    
    @staticmethod
    def sanitize_text_input(text: str, max_length: int = 2000) -> str:
        """
        Sanitize user text input to prevent injection attacks
        """
        if not text:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Length check
        if len(text) > max_length:
            raise HTTPException(
                status_code=400,
                detail=f"Message too long: {len(text)} chars (max {max_length})"
            )
        
        # Basic XSS prevention (if storing in DB)
        dangerous_chars = ['<script', '<iframe', 'javascript:', 'onerror=']
        text_lower = text.lower()
        
        for dangerous in dangerous_chars:
            if dangerous in text_lower:
                raise HTTPException(
                    status_code=400,
                    detail="Message contains potentially dangerous content"
                )
        
        return text.strip()


# Rate limiting helper (requires Redis in production)
class RateLimiter:
    """
    Simple in-memory rate limiter
    In production: use Redis with sliding window algorithm
    """
    
    _requests = {}  # client_id -> (count, reset_time)
    
    @staticmethod
    def check_rate_limit(
        client_id: str,
        max_requests: int = 10,
        window_seconds: int = 60
    ) -> bool:
        """
        Check if client has exceeded rate limit
        Returns True if allowed, raises HTTPException if exceeded
        """
        import time
        
        current_time = time.time()
        
        if client_id not in RateLimiter._requests:
            RateLimiter._requests[client_id] = (1, current_time + window_seconds)
            return True
        
        count, reset_time = RateLimiter._requests[client_id]
        
        # Window expired, reset
        if current_time > reset_time:
            RateLimiter._requests[client_id] = (1, current_time + window_seconds)
            return True
        
        # Increment counter
        if count >= max_requests:
            raise RateLimitError(
                message=f"Rate limit exceeded. Try again in {int(reset_time - current_time)} seconds",
                details={
                    "max_requests": max_requests,
                    "window_seconds": window_seconds,
                    "retry_after": int(reset_time - current_time)
                }
            )
        
        RateLimiter._requests[client_id] = (count + 1, reset_time)
        return True
