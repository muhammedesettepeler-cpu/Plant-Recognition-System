"""
Kaggle Notebook Integration Service
Sends user images to Kaggle for processing with PlantCLEF dataset
"""
import os
import httpx
from typing import Dict, Any, List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class KaggleNotebookService:
    """
    Kaggle Notebook API integration
    Uses Kaggle notebook as inference server for PlantCLEF 2025 dataset
    """
    
    def __init__(self):
        self.notebook_url = os.getenv("KAGGLE_NOTEBOOK_URL", "")
        self.timeout = 30.0  # 30 seconds timeout
        self._available = False
        
    async def check_availability(self) -> bool:
        """Check if Kaggle notebook API is available"""
        if not self.notebook_url:
            logger.warning("Kaggle notebook URL not configured")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.notebook_url}/health",
                    timeout=5.0
                )
                self._available = response.status_code == 200
                return self._available
        except Exception as e:
            logger.error(f"Kaggle notebook health check failed: {e}")
            self._available = False
            return False
    
    async def identify_plant(self, image_bytes: bytes, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Identify plant using Kaggle notebook inference API
        
        Args:
            image_bytes: Image file bytes
            top_k: Number of top predictions to return
        
        Returns:
            List of predictions:
            [
                {
                    "species": "Rosa damascena",
                    "confidence": 0.95,
                    "common_name": "Damascus Rose",
                    "source": "kaggle-plantclef"
                },
                ...
            ]
        """
        if not self.notebook_url:
            logger.error("Kaggle notebook URL not configured")
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                files = {"image": ("plant.jpg", image_bytes, "image/jpeg")}
                data = {"top_k": str(top_k)}
                
                response = await client.post(
                    f"{self.notebook_url}/predict",
                    files=files,
                    data=data,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    predictions = result.get("predictions", [])
                    
                    # Add source tag and format for compatibility
                    formatted_predictions = []
                    for pred in predictions:
                        formatted_predictions.append({
                            "scientificName": pred.get("species", "Unknown"),
                            "commonName": pred.get("common_name", pred.get("species", "Unknown")),
                            "score": pred.get("confidence", 0.0),
                            "certainty": pred.get("confidence", 0.0),
                            "source": "kaggle-plantclef",
                            "model": result.get("model", "PlantCLEF-2025"),
                            "inference_time": result.get("inference_time", 0)
                        })
                    
                    logger.info(f"Kaggle prediction successful: {len(formatted_predictions)} results")
                    return formatted_predictions
                else:
                    logger.error(f"Kaggle prediction failed: {response.status_code}")
                    return []
                    
        except httpx.TimeoutException:
            logger.error("Kaggle notebook request timeout")
            return []
        except Exception as e:
            logger.error(f"Kaggle prediction error: {e}")
            return []
    
    @property
    def is_available(self) -> bool:
        """Check if service is available"""
        return bool(self.notebook_url) and self._available

kaggle_notebook_service = KaggleNotebookService()
