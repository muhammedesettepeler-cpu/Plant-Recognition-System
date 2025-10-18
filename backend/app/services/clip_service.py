from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch
from typing import List, Union
import io
from app.core.config import settings
from app.core.exceptions import CLIPModelError
import logging

logger = logging.getLogger(__name__)

class CLIPService:
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_model(self):
        try:
            logger.info("Loading CLIP model...")
            self.model = CLIPModel.from_pretrained(settings.CLIP_MODEL_NAME)
            self.processor = CLIPProcessor.from_pretrained(settings.CLIP_MODEL_NAME)
            self.model.to(self.device)
            self.model.eval()
            logger.info(f"CLIP model loaded successfully on {self.device}")
            return True
        except Exception as e:
            logger.error(f"CLIP model loading failed: {e}", exc_info=True)
            raise CLIPModelError(
                message="Failed to load CLIP model",
                details={"error": str(e), "model": settings.CLIP_MODEL_NAME}
            )
    
    def encode_image(self, image: Union[Image.Image, bytes]) -> List[float]:
        """
        Extract normalized image embedding using CLIP.
        Pipeline: Image -> RGB conversion -> CLIP preprocessing -> Model inference -> L2 normalization
        """
        try:
            if self.model is None:
                logger.info("CLIP model not loaded, loading now...")
                self.load_model()
            
            if isinstance(image, bytes):
                image = Image.open(io.BytesIO(image))
            
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                features = self.model.get_image_features(**inputs)
                features = features / features.norm(dim=-1, keepdim=True)
            
            return features.cpu().numpy().flatten().tolist()
        except CLIPModelError:
            raise
        except Exception as e:
            logger.error(f"Image encoding failed: {e}", exc_info=True)
            raise CLIPModelError(
                message="Failed to encode image with CLIP",
                details={"error": str(e)}
            )
    
    def encode_text(self, text: str) -> List[float]:
        """
        Extract normalized text embedding using CLIP.
        Used for semantic search: text query -> find similar plant images
        """
        try:
            if self.model is None:
                if not self.load_model():
                    raise Exception("Failed to load CLIP model")
            
            inputs = self.processor(text=[text], return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                features = self.model.get_text_features(**inputs)
                features = features / features.norm(dim=-1, keepdim=True)
            
            return features.cpu().numpy().flatten().tolist()
        except Exception as e:
            print(f"Text encode error: {e}")
            return None

clip_service = CLIPService()
