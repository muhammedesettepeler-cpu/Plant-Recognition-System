from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.services.clip_service import clip_service
from app.services.weaviate_service import weaviate_service
from app.services.plantnet_service import plantnet_service
from app.services.grok_service import grok_service
from app.utils.image_utils import image_processor
from app.core.config import settings
from PIL import Image
import io

router = APIRouter()

@router.post("/recognize")
async def recognize_plant(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    image_bytes = await file.read()
    is_valid, message = image_processor.validate_image(image_bytes)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    try:
        # PlantNet identification
        plantnet_results = await plantnet_service.identify_plant(image_bytes)
        
        # CLIP similarity search
        pil_image = Image.open(io.BytesIO(image_bytes))
        embedding = clip_service.encode_image(pil_image)
        similar_plants = weaviate_service.similarity_search(embedding) if embedding else []
        
        # Get top result
        top_plant = None
        if plantnet_results["success"] and plantnet_results["results"]:
            top = plantnet_results["results"][0]
            top_plant = {
                "scientific_name": top["scientific_name"],
                "family": top.get("family"),
                "confidence": top["score"]
            }
        
        # Generate description
        description = None
        if top_plant:
            description = await grok_service.generate_response(
                f"Briefly describe {top_plant['scientific_name']}"
            )
        
        return {
            "success": True,
            "plantnet_results": plantnet_results,
            "similarity_results": similar_plants,
            "top_match": top_plant,
            "description": description
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
