import httpx
from app.core.config import settings

class PlantNetService:
    def __init__(self):
        self.api_key = settings.PLANTNET_API_KEY
        self.api_url = settings.PLANTNET_API_URL
    
    async def identify_plant(self, image_data: bytes):
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
            print(f"PlantNet error: {e}")
            return {"success": False, "results": []}

plantnet_service = PlantNetService()
