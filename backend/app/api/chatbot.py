from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Header, Request
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, UTC
from app.db.base import get_db
from app.services.grok_service import grok_service
from app.services.clip_service import clip_service
from app.services.weaviate_service import weaviate_service
from app.services.kaggle_notebook_service import kaggle_notebook_service
from app.models.plant import UserQuery
from app.core.security import ImageSecurity, AuthSecurity
from app.core.rate_limiter import rate_limiter  # Yeni Redis-powered rate limiter
from app.core.config import settings
from app.core.exceptions import (
    exception_to_http,
    CLIPModelError,
    WeaviateConnectionError,
    LLMServiceError,
    ImageValidationError,
    DatabaseError,
    PlantRecognitionException
)
import uuid
from datetime import datetime
from PIL import Image
import io
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

@router.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # Check if plant-related
        keywords = ["plant", "flower", "tree", "leaf"]
        is_plant_query = any(k in request.message.lower() for k in keywords)
        
        relevant_plants = []
        if is_plant_query:
            text_embedding = clip_service.encode_text(request.message)
            if text_embedding:
                relevant_plants = weaviate_service.similarity_search(text_embedding, limit=3)
        
        # Generate response
        if relevant_plants:
            response = await grok_service.generate_rag_response(request.message, relevant_plants)
        else:
            response = await grok_service.generate_response(request.message)
        
        # Log to database
        query = UserQuery(
            session_id=session_id,
            query_type="text",
            query_text=request.message,
            response=response
        )
        db.add(query)
        db.commit()
        
        return {
            "session_id": session_id,
            "response": response,
            "relevant_plants": relevant_plants if relevant_plants else None,
            "timestamp": datetime.now(UTC).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat-with-image")
async def chat_with_image(
    request: Request,
    file: UploadFile = File(...),
    message: str = Form(...),
    session_id: Optional[str] = Form(None),
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    _rate_limit: None = Depends(rate_limiter)  # Redis-powered rate limiting
):
    """
     SECURE RAG Pipeline for Image-based Plant Questions
    
    Security Layers:
    1. API Key Authentication (optional, configurable)
    2. Rate Limiting (per IP/client)
    3. Image Validation (size, MIME type, magic bytes)
    4. PIL Verification (exploit detection)
    5. Content Sanitization (EXIF removal, re-encoding)
    6. Text Input Sanitization (XSS prevention)
    7. Dimension Limits (4096x4096 max)
    8. All API keys stay in backend (never exposed)
    
    Pipeline Flow:
    1. Frontend sends FormData (binary image + text message)
    2. Backend validates and sanitizes everything
    3. CLIP Processor preprocesses image
    4. CLIP Model extracts normalized embedding
    5. Weaviate similarity search finds top-k matches
    6. Matched plant data used as RAG context
    7. LLM (OpenRouter) generates detailed response with context
    8. All sensitive operations happen in backend only
    """
    
    client_id = request.client.host if request.client else "unknown"
    
    try:
        # SECURITY LAYER 1: API Key Authentication
        if settings.REQUIRE_API_KEY:
            await AuthSecurity.verify_api_key(x_api_key)
            logger.info(f"API key validated for client {client_id}")
        
        # SECURITY LAYER 2: Rate Limiting (handled by Depends(rate_limiter))
        # Automatically blocks requests if limit exceeded
        logger.info(f"Rate limit check passed for client {client_id}")
        
        # SECURITY LAYER 3-5: Image Validation
        is_valid, error_msg, sanitized_bytes = await ImageSecurity.validate_image(
            file,
            max_size_mb=settings.MAX_IMAGE_SIZE_MB
        )
        logger.info(f"Image validated and sanitized: {len(sanitized_bytes)} bytes")
        
        # SECURITY LAYER 6: Text Input Sanitization
        safe_message = AuthSecurity.sanitize_text_input(message, max_length=2000)
        logger.info(f"Text sanitized: {len(safe_message)} chars")
        session_id = session_id or str(uuid.uuid4())
        
        # Compute image hash for duplicate detection (optional)
        image_hash = ImageSecurity.compute_image_hash(sanitized_bytes)
        logger.info(f"📸 Image hash: {image_hash[:16]}...")
        
        # STEP 1: Load sanitized image
        pil_image = Image.open(io.BytesIO(sanitized_bytes))
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")
        logger.info(f"🖼️ Image loaded: {pil_image.size}, mode={pil_image.mode}")
        
        # STEP 2-3: CLIP preprocessing + embedding extraction (normalized)
        # 🔒 CLIP service runs ONLY in backend, API keys never exposed
        embedding = clip_service.encode_image(pil_image)
        if not embedding:
            raise HTTPException(status_code=500, detail="Failed to extract image features")
        logger.info(f"🧠 CLIP embedding extracted: {len(embedding)} dimensions")
        
        # STEP 4: Weaviate vector similarity search
        # 🔒 Weaviate credentials stay in backend only
        similar_plants = weaviate_service.similarity_search(embedding, limit=5)
        logger.info(f"🔍 Weaviate found {len(similar_plants)} similar plants")
        
        # STEP 4.5: Fallback to Kaggle if Weaviate results are poor
        # Use Kaggle PlantCLEF 2025 dataset (1TB+, 10k+ species) for better coverage
        kaggle_results = []
        if not similar_plants or (similar_plants and similar_plants[0].get('_additional', {}).get('certainty', 0) < 0.7):
            logger.info("🎯 Weaviate confidence low, trying Kaggle PlantCLEF...")
            try:
                kaggle_results = await kaggle_notebook_service.identify_plant(sanitized_bytes, top_k=5)
                if kaggle_results:
                    logger.info(f"✅ Kaggle found {len(kaggle_results)} predictions")
                    # Merge results: Kaggle results have higher priority if confidence is high
                    if kaggle_results[0].get('certainty', 0) > 0.8:
                        similar_plants = kaggle_results + similar_plants
                        logger.info("📊 Using Kaggle results as primary source")
            except Exception as e:
                logger.warning(f"Kaggle prediction failed: {e}, continuing with Weaviate only")
        
        # Combine all sources
        all_results = similar_plants[:5]  # Top 5 from combined sources
        logger.info(f"📊 Total results: {len(all_results)}")
        
        # STEP 5-6: RAG - Use top matches as context for LLM
        if all_results:
            # En iyi 3 sonucu formatla
            top_3 = all_results[:3]
            context = "\n".join([
                f"- {p.get('scientificName', 'Unknown')} ({p.get('commonName', '')}): "
                f"{p.get('certainty', p.get('score', 0)):.2%} confidence, "
                f"Family: {p.get('family', 'Unknown')}"
                for p in top_3
            ])
            
            # Türkçe prompt oluştur
            if safe_message.lower() in ['identify', 'tanı', 'nedir', 'what is']:
                prompt = (f"Aşağıdaki bitki türlerinden hangisi olduğunu açıkla. "
                         f"3 seçeneği detaylı anlat:\n{context}")
            else:
                prompt = f"Bitki veritabanı sonuçları:\n{context}\n\nKullanıcı sorusu: {safe_message}"
            
            # LLM yanıtı al (hata durumunda fallback bitki bilgisiyle çalışır)
            response = await grok_service.generate_rag_response(prompt, top_3)
            logger.info(f"💬 LLM response generated: {len(response)} chars")
        else:
            response = ("Görsel analizi tamamlandı ancak veritabanında eşleşen bitki bulunamadı. "
                       "Lütfen daha net bir fotoğraf veya farklı açıdan çekilmiş görsel deneyin.")
            logger.info("💬 No plants found, returning info message")
        
        # STEP 7: Log to database
        query = UserQuery(
            session_id=session_id,
            query_type="image",
            query_text=safe_message,
            response=response
        )
        db.add(query)
        db.commit()
        logger.info(f"💾 Query logged to database: session {session_id}")
        
        # STEP 8: Return response with formatted plant data
        formatted_plants = []
        for idx, plant in enumerate(all_results[:3], 1):
            # Weaviate certainty değeri _additional nesnesinde
            additional = plant.get('_additional', {})
            certainty = additional.get('certainty', plant.get('certainty', plant.get('score', 0)))
            
            # Eğer certainty hala 0 ise distance'dan hesapla (cosine distance: 0-2, 0=aynı)
            if certainty == 0 and 'distance' in additional:
                distance = additional.get('distance', 2)
                certainty = 1 - (distance / 2)  # Distance'ı certainty'ye çevir (0-1)
            
            formatted_plant = {
                "id": idx,
                "scientificName": plant.get('scientificName', 'Bilinmeyen'),
                "commonName": plant.get('commonName', ''),
                "family": plant.get('family', ''),
                "confidence": max(0.0, min(1.0, certainty)),  # 0-1 arasında sınırla
                "source": plant.get('source', 'weaviate')
            }
            
            # Eğer ek bilgi varsa ekle
            if plant.get('description'):
                formatted_plant['description'] = plant.get('description')
            if plant.get('habitat'):
                formatted_plant['habitat'] = plant.get('habitat')
            
            formatted_plants.append(formatted_plant)
            
            # Debug log
            logger.info(f"Plant {idx}: {formatted_plant['scientificName']} - "
                       f"Confidence: {formatted_plant['confidence']:.2%} "
                       f"(raw certainty: {additional.get('certainty')}, distance: {additional.get('distance')})")
        
        return {
            "session_id": session_id,
            "response": response,
            "identified_plants": formatted_plants,
            "total_matches": len(all_results),
            "highest_confidence": formatted_plants[0]["confidence"] if formatted_plants else 0,
            "sources": {
                "weaviate": len([p for p in all_results if p.get('source') != 'kaggle-plantclef']),
                "kaggle": len([p for p in all_results if p.get('source') == 'kaggle-plantclef'])
            },
            "image_hash": image_hash[:16],
            "timestamp": datetime.now(UTC).isoformat()
        }
        
    except HTTPException:
        raise
    except PlantRecognitionException as e:
        logger.error(f"Plant recognition error: {e.message}", exc_info=True)
        raise exception_to_http(e)
    except Exception as e:
        logger.error(f"Unexpected error in chat-with-image: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": str(e),
                "type": "UnexpectedError"
            }
        )
