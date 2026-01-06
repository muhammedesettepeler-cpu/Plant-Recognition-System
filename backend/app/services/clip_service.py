from transformers import CLIPProcessor, CLIPModel
from PIL import Image, ImageEnhance, ImageFilter
import torch
from typing import List, Union
import io
import numpy as np
from app.core.config import settings
from app.core.exceptions import CLIPModelError
import logging

logger = logging.getLogger(__name__)

class CLIPService:
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
    
    def _advanced_preprocessing(self, image: Image.Image) -> Image.Image:
        """
        Advanced image preprocessing for better plant recognition:
        1. Denoise (reduce image noise)
        2. Enhance sharpness (make edges clearer)
        3. Auto contrast (normalize brightness/contrast)
        4. Color enhancement (make plant colors more vivid)
        """
        try:
            # Step 1: Denoise - reduce noise from camera sensor
            image = image.filter(ImageFilter.MedianFilter(size=3))
            
            # Step 2: Enhance sharpness - make plant details clearer
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.3)  # 30% sharper
            
            # Step 3: Auto contrast - normalize brightness
            # Convert to numpy for percentile calculation
            img_array = np.array(image)
            
            # Calculate 2nd and 98th percentile for robust normalization
            p2, p98 = np.percentile(img_array, (2, 98))
            
            # Normalize to full range if needed
            if p98 - p2 > 0:
                img_array = np.clip((img_array - p2) * 255.0 / (p98 - p2), 0, 255).astype(np.uint8)
                image = Image.fromarray(img_array)
            
            # Step 4: Enhance color - make plant colors more distinguishable
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.2)  # 20% more saturated
            
            logger.debug(" Advanced preprocessing applied: denoise, sharpen, contrast, color enhance")
            return image
            
        except Exception as e:
            logger.warning(f"Advanced preprocessing failed, using original: {e}")
            return image
    
    def _multi_crop_augmentation(self, image: Image.Image) -> List[Image.Image]:
        """
        Multi-crop strategy for test-time augmentation:
        - Center crop
        - 4 corner crops
        This helps recognize plants from different angles/positions
        """
        width, height = image.size
        crop_size = min(width, height)
        
        crops = []
        
        # Center crop
        left = (width - crop_size) // 2
        top = (height - crop_size) // 2
        crops.append(image.crop((left, top, left + crop_size, top + crop_size)))
        
        # Top-left
        crops.append(image.crop((0, 0, crop_size, crop_size)))
        
        # Top-right
        crops.append(image.crop((width - crop_size, 0, width, crop_size)))
        
        # Bottom-left
        crops.append(image.crop((0, height - crop_size, crop_size, height)))
        
        # Bottom-right
        crops.append(image.crop((width - crop_size, height - crop_size, width, height)))
        
        return crops
        
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
    
    def encode_image(self, image: Union[Image.Image, bytes], use_tta: bool = True) -> List[float]:
        """
        Extract normalized image embedding using CLIP with advanced preprocessing.
        
        Pipeline:
        1. Image -> RGB conversion
        2. Advanced preprocessing (denoise, sharpen, contrast, color)
        3. Multi-crop augmentation (optional, enabled by default)
        4. CLIP preprocessing -> Model inference
        5. Ensemble averaging + L2 normalization
        
        Args:
            image: PIL Image or bytes
            use_tta: Use Test-Time Augmentation (multi-crop) for better accuracy
        
        Returns:
            Normalized embedding vector
        """
        try:
            if self.model is None:
                logger.info("CLIP model not loaded, loading now...")
                self.load_model()
            
            # Convert bytes to PIL Image
            if isinstance(image, bytes):
                image = Image.open(io.BytesIO(image))
            
            # Convert to RGB
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            # Apply advanced preprocessing
            logger.info(" Applying advanced preprocessing...")
            image = self._advanced_preprocessing(image)
            
            # Test-Time Augmentation with multi-crop
            if use_tta and min(image.size) > 300:  # Only for larger images
                logger.info(" Using multi-crop TTA for better accuracy...")
                crops = self._multi_crop_augmentation(image)
                
                # Extract embeddings for all crops
                all_embeddings = []
                for idx, crop in enumerate(crops):
                    inputs = self.processor(images=crop, return_tensors="pt")
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    
                    with torch.no_grad():
                        features = self.model.get_image_features(**inputs)
                        features = features / features.norm(dim=-1, keepdim=True)
                        all_embeddings.append(features)
                
                # Average all embeddings (ensemble)
                final_features = torch.stack(all_embeddings).mean(dim=0)
                # Re-normalize after averaging
                final_features = final_features / final_features.norm(dim=-1, keepdim=True)
                
                logger.info(f" TTA complete: averaged {len(crops)} crops")
            else:
                # Standard single-crop encoding
                inputs = self.processor(images=image, return_tensors="pt")
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    final_features = self.model.get_image_features(**inputs)
                    final_features = final_features / final_features.norm(dim=-1, keepdim=True)
            
            return final_features.cpu().numpy().flatten().tolist()
            
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
