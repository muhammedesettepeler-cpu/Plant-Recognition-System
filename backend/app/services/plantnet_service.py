import httpx
from app.core.config import settings
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class PlantNetService:
    def __init__(self):
        self.api_key = settings.PLANTNET_API_KEY
        self.api_url = settings.PLANTNET_API_URL
    
    async def identify_plant(self, image_data: bytes):
        """Identify plant from image and return basic results"""
        try:
            files = {"images": ("plant.jpg", image_data, "image/jpeg")}
            params = {"api-key": self.api_key}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.api_url, files=files, params=params)
                response.raise_for_status()
                result = response.json()
                
                # Simple parse
                plants = []
                for r in result.get("results", [])[:3]:
                    plants.append({
                        "scientific_name": r["species"]["scientificNameWithoutAuthor"],
                        "family": r["species"].get("family", {}).get("scientificNameWithoutAuthor"),
                        "score": r["score"]
                    })
                return {"success": True, "results": plants}
        except Exception as e:
            logger.error(f"PlantNet identify error: {e}")
            return {"success": False, "results": []}
    
    async def get_plant_details(self, scientific_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed plant information from PlantNet API by scientific name.
        This searches PlantNet's database for the given species.
        
        Returns detailed info: common names, family, images, habitat, etc.
        """
        if not self.api_key:
            logger.warning("PlantNet API key not configured")
            return None
        
        try:
            # PlantNet doesn't have a direct "get by name" endpoint,
            # but we can use their search API or rely on previous identification results
            # For now, we'll return structured data that can be enhanced with other APIs
            
            # Fallback: Return basic structure that will be filled by other sources
            logger.info(f"PlantNet: Would fetch details for {scientific_name}")
            
            # TODO: Integrate with additional botanical APIs (GBIF, Wikipedia, etc.)
            # For now, return None to indicate no data available
            return None
            
        except Exception as e:
            logger.error(f"PlantNet get_plant_details error: {e}")
            return None
    
    async def get_detailed_results(self, image_data: bytes, top_k: int = 3) -> list:
        """
        Get detailed plant identification results with all available information.
        Returns: List of dicts with scientific_name, common_names, family, description, images, score
        """
        if not self.api_key:
            logger.warning("PlantNet API key not configured, skipping")
            return []
        
        try:
            files = {"images": ("plant.jpg", image_data, "image/jpeg")}
            params = {"api-key": self.api_key}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.api_url, files=files, params=params)
                response.raise_for_status()
                result = response.json()
                
                # Detailed parse with all available information
                plants = []
                for r in result.get("results", [])[:top_k]:
                    species = r.get("species", {})
                    
                    plant_data = {
                        "scientific_name": species.get("scientificNameWithoutAuthor", "Unknown"),
                        "scientific_name_full": species.get("scientificName", ""),
                        "common_names": species.get("commonNames", []),
                        "family": species.get("family", {}).get("scientificNameWithoutAuthor", ""),
                        "genus": species.get("genus", {}).get("scientificName", ""),
                        "score": r.get("score", 0),
                        "images": [img.get("url", {}).get("o", "") for img in r.get("images", [])[:3]],
                        "gbif_id": r.get("gbif", {}).get("id"),
                    }
                    
                    plants.append(plant_data)
                    logger.info(f"PlantNet found: {plant_data['scientific_name']} (score: {plant_data['score']:.2f})")
                
                return plants
                
        except httpx.HTTPStatusError as e:
            logger.error(f"PlantNet API HTTP error: {e.response.status_code}")
            return []
        except Exception as e:
            logger.error(f"PlantNet detailed results error: {e}")
            return []

plantnet_service = PlantNetService()
