from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    UploadFile,
    File,
    Form,
    Header,
    Request,
)
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, UTC
from app.services.grok_service import grok_service
from app.services.kaggle_notebook_service import kaggle_notebook_service
from app.services.plantnet_service import plantnet_service
from app.services.usda_service import usda_service
from app.core.security import ImageSecurity, AuthSecurity
from app.core.rate_limiter import rate_limiter
from app.core.config import settings
from app.core.exceptions import (
    exception_to_http,
    LLMServiceError,
    ImageValidationError,
    PlantRecognitionException,
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
async def chat(request: ChatRequest):
    """Text-only chat endpoint - uses LLM directly"""
    session_id = request.session_id or str(uuid.uuid4())

    try:
        # Generate response using LLM
        response = await grok_service.generate_response(request.message)

        # Note: Database logging disabled (no PostgreSQL)

        return {
            "session_id": session_id,
            "response": response,
            "timestamp": datetime.now(UTC).isoformat(),
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
    _rate_limit: None = Depends(rate_limiter),
):
    """
    🌿 HYBRID RAG Pipeline for Plant Recognition

    Flow:
    1. Kaggle PlantCLEF API → Image-based plant identification (1.5TB remote)
    2. PlantNet API → General plant information (primary info source)
    3. USDA Service → Validation + additional info (93K local plants)
    4. LLM (Gemini/OpenRouter) → Turkish explanation generation

    Security Layers:
    1. API Key Authentication (optional)
    2. Rate Limiting (Redis-powered)
    3. Image Validation (size, MIME, magic bytes)
    4. PIL Verification + Content Sanitization
    5. Text Input Sanitization
    """

    client_id = request.client.host if request.client else "unknown"

    try:
        # SECURITY LAYER 1: API Key Authentication
        if settings.REQUIRE_API_KEY:
            await AuthSecurity.verify_api_key(x_api_key)
            logger.info(f"✅ API key validated for client {client_id}")

        # SECURITY LAYER 2: Rate Limiting (handled by Depends)
        logger.info(f"✅ Rate limit check passed for client {client_id}")

        # SECURITY LAYER 3-5: Image Validation & Sanitization
        is_valid, error_msg, sanitized_bytes = await ImageSecurity.validate_image(
            file, max_size_mb=settings.MAX_IMAGE_SIZE_MB
        )
        logger.info(f"✅ Image validated: {len(sanitized_bytes)} bytes")

        # SECURITY LAYER 6: Text Input Sanitization
        safe_message = AuthSecurity.sanitize_text_input(message, max_length=2000)
        session_id = session_id or str(uuid.uuid4())

        # Image hash for duplicate detection
        image_hash = ImageSecurity.compute_image_hash(sanitized_bytes)
        logger.info(f"📸 Image hash: {image_hash[:16]}...")

        # Load image
        pil_image = Image.open(io.BytesIO(sanitized_bytes))
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")
        logger.info(f"🖼️ Image loaded: {pil_image.size}")

        # ═══════════════════════════════════════════════════════════════
        # STEP 1: KAGGLE PLANTCLEF API - Image-based plant identification
        # ═══════════════════════════════════════════════════════════════
        kaggle_results = []
        try:
            logger.info("🔍 Querying Kaggle PlantCLEF API...")
            kaggle_results = await kaggle_notebook_service.identify_plant(
                sanitized_bytes, top_k=5
            )
            if kaggle_results:
                logger.info(f"✅ Kaggle found {len(kaggle_results)} predictions")
            else:
                logger.warning("⚠️ Kaggle returned no results")
        except Exception as e:
            logger.warning(f"⚠️ Kaggle API failed: {e}")

        # ═══════════════════════════════════════════════════════════════
        # STEP 2: PLANTNET API - General plant information
        # ═══════════════════════════════════════════════════════════════
        plantnet_results = []
        try:
            logger.info("🌱 Querying PlantNet API for general info...")
            plantnet_results = await plantnet_service.identify_plant(sanitized_bytes)
            if plantnet_results:
                logger.info(f"✅ PlantNet found {len(plantnet_results)} results")
            else:
                logger.warning("⚠️ PlantNet returned no results")
        except Exception as e:
            logger.warning(f"⚠️ PlantNet API failed: {e}")

        # ═══════════════════════════════════════════════════════════════
        # STEP 3: COMBINE & VALIDATE WITH USDA
        # ═══════════════════════════════════════════════════════════════
        combined_results = []

        # Merge results: prioritize Kaggle for identification, PlantNet for info
        primary_source = kaggle_results if kaggle_results else plantnet_results

        # Ensure primary_source is a list (not None or dict)
        if primary_source is None:
            primary_source = []
        elif isinstance(primary_source, dict):
            primary_source = [primary_source]
        elif not isinstance(primary_source, list):
            primary_source = []

        for result in list(primary_source)[:5]:
            scientific_name = result.get(
                "scientificName", result.get("scientific_name", "Unknown")
            )

            # Start with base info
            enriched_result = {
                "scientificName": scientific_name,
                "commonName": result.get("commonName", result.get("common_name", "")),
                "family": result.get("family", ""),
                "confidence": result.get("certainty", result.get("score", 0)),
                "source": result.get("source", "plantnet"),
                "usda_verified": False,
            }

            # USDA validation and enrichment
            usda_data = usda_service.find_by_scientific_name(scientific_name)
            if usda_data:
                enriched_result["usda_verified"] = True
                enriched_result["usda_symbol"] = usda_data["symbol"]
                # Fill missing info from USDA
                if not enriched_result["family"]:
                    enriched_result["family"] = usda_data["family"]
                if not enriched_result["commonName"]:
                    enriched_result["commonName"] = usda_data["common_name"]
                logger.info(f"✅ USDA verified: {scientific_name}")
            else:
                logger.info(f"ℹ️ {scientific_name} not in USDA database")

            # Cross-reference with PlantNet for additional info
            if kaggle_results and plantnet_results:
                for pn in plantnet_results:
                    # Skip if pn is not a dict (could be string in some error cases)
                    if not isinstance(pn, dict):
                        continue
                    pn_name = pn.get("scientific_name", "") or pn.get(
                        "scientificName", ""
                    )
                    if pn_name and scientific_name.lower().startswith(
                        pn_name.lower().split()[0] if pn_name else ""
                    ):
                        # Found matching genus, add PlantNet info
                        enriched_result["genus"] = pn.get("genus", "")
                        if pn.get("common_name") and not enriched_result["commonName"]:
                            enriched_result["commonName"] = pn.get("common_name")
                        break

            combined_results.append(enriched_result)

        logger.info(f"📊 Combined {len(combined_results)} plant results")

        # ═══════════════════════════════════════════════════════════════
        # STEP 4: LLM RAG - Generate Turkish explanation
        # ═══════════════════════════════════════════════════════════════
        if combined_results:
            top_3 = combined_results[:3]
            context_parts = []

            for p in top_3:
                confidence = p.get("confidence", 0)
                usda_status = (
                    "✓ USDA Doğrulandı" if p.get("usda_verified") else "Doğrulanmadı"
                )

                context = (
                    f"- {p['scientificName']} ({p['commonName']})\n"
                    f"  Aile: {p.get('family', 'Bilinmiyor')}\n"
                    f"  Güven: {confidence:.1%}\n"
                    f"  Kaynak: {p.get('source', 'unknown')}, {usda_status}"
                )
                context_parts.append(context)

            context = "\n\n".join(context_parts)

            # Build prompt based on user query
            if safe_message.lower() in [
                "identify",
                "tanı",
                "nedir",
                "what is",
                "bu ne",
            ]:
                prompt = (
                    f"Yüklenen bitkinin türünü belirle ve Türkçe açıkla.\n\n"
                    f"BULUNAN BİTKİLER:\n{context}\n\n"
                    f"GÖREV: Her bitki için kısa açıklama yap (isim, güven, özellikler)."
                )
            else:
                prompt = (
                    f"Kullanıcı sorusu: {safe_message}\n\n"
                    f"BULUNAN BİTKİLER:\n{context}\n\n"
                    f"GÖREV: Soruyu bu bitki bilgileriyle cevaplayarak Türkçe yanıt ver."
                )

            response = await grok_service.generate_rag_response(prompt, context, top_3)
            logger.info(f"✅ LLM response: {len(response)} chars")
        else:
            response = (
                "Görsel analizi tamamlandı ancak eşleşen bitki bulunamadı. "
                "Lütfen daha net bir fotoğraf veya farklı açıdan çekilmiş görsel deneyin."
            )
            logger.info("⚠️ No plants found")

        # ═══════════════════════════════════════════════════════════════
        # STEP 5: Log to database & return response
        # ═══════════════════════════════════════════════════════════════
        # Note: Database logging disabled (no PostgreSQL)
        logger.info(f"💾 Query processed: session {session_id}")

        # Format response
        formatted_plants = []
        for idx, plant in enumerate(combined_results[:3], 1):
            formatted_plants.append(
                {
                    "id": idx,
                    "scientificName": plant.get("scientificName", "Unknown"),
                    "commonName": plant.get("commonName", ""),
                    "family": plant.get("family", ""),
                    "confidence": max(0.0, min(1.0, plant.get("confidence", 0))),
                    "source": plant.get("source", "unknown"),
                    "usda_verified": plant.get("usda_verified", False),
                }
            )

        return {
            "session_id": session_id,
            "response": response,
            "identified_plants": formatted_plants,
            "total_matches": len(combined_results),
            "highest_confidence": formatted_plants[0]["confidence"]
            if formatted_plants
            else 0,
            "sources": {
                "kaggle": len(
                    [
                        p
                        for p in combined_results
                        if p.get("source") == "kaggle-plantclef"
                    ]
                ),
                "plantnet": len(
                    [
                        p
                        for p in combined_results
                        if p.get("source") != "kaggle-plantclef"
                    ]
                ),
                "usda_verified": len(
                    [p for p in combined_results if p.get("usda_verified")]
                ),
            },
            "image_hash": image_hash[:16],
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except HTTPException:
        raise
    except PlantRecognitionException as e:
        logger.error(f"Plant recognition error: {e.message}", exc_info=True)
        raise exception_to_http(e)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "message": str(e)},
        )
