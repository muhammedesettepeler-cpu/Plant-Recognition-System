import cv2
import numpy as np
from PIL import Image
import io

class ImageProcessor:
    @staticmethod
    def resize_image(image: Image.Image, max_size=(800, 800)) -> Image.Image:
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        return image
    
    @staticmethod
    def enhance_image(image_bytes: bytes) -> bytes:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Denoise
        img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        
        _, buffer = cv2.imencode('.jpg', img)
        return buffer.tobytes()
    
    @staticmethod
    def validate_image(image_bytes: bytes, max_size_mb=10):
        size_mb = len(image_bytes) / (1024 * 1024)
        if size_mb > max_size_mb:
            return False, f"Image too large ({size_mb:.2f}MB)"
        
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.verify()
            return True, "Valid"
        except:
            return False, "Invalid image"

image_processor = ImageProcessor()
