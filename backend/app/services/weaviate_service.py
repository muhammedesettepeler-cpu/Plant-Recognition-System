import weaviate
from weaviate.auth import AuthApiKey
from typing import List, Dict, Any
from datetime import datetime, UTC
from app.core.config import settings
from app.core.exceptions import WeaviateConnectionError
import logging

logger = logging.getLogger(__name__)

class WeaviateService:
    def __init__(self):
        self.client = None
        self.class_name = "PlantImage"
        
    def connect(self):
        """Connect to Weaviate Cloud (v3 API)"""
        try:
            if settings.WEAVIATE_API_KEY:
                auth_config = AuthApiKey(api_key=settings.WEAVIATE_API_KEY)
                
                self.client = weaviate.Client(
                    url=settings.WEAVIATE_URL,
                    auth_client_secret=auth_config,
                    timeout_config=(10, 60)
                )
                
                if self.client.is_ready():
                    logger.info("Weaviate connection established successfully")
                    return True
                else:
                    logger.error("Weaviate client not ready")
                    return False
            else:
                self.client = weaviate.Client(url=settings.WEAVIATE_URL)
                return self.client.is_ready()
        except Exception as e:
            logger.error(f"Weaviate connection error: {e}", exc_info=True)
            raise WeaviateConnectionError(
                message="Failed to connect to Weaviate Cloud",
                details={"error": str(e), "url": settings.WEAVIATE_URL}
            )
    
    def create_schema(self, force_recreate: bool = False):
        """
        Create or update PlantImage schema in Weaviate.
        
        Schema Properties:
        - plantId: Unique plant identifier (int)
        - scientificName: Scientific name (e.g., "Rosa gallica")
        - commonName: Common name (e.g., "French Rose")
        - family: Plant family (e.g., "Rosaceae")
        - imageUrl: URL or path to the image
        - description: Plant description (optional)
        - createdAt: Timestamp when added
        
        Vector: 512-dimensional CLIP embedding (cosine similarity)
        """
        schema = {
            "class": self.class_name,
            "description": "Plant images with CLIP embeddings for similarity search",
            "vectorizer": "none",  # We provide our own vectors from CLIP
            "vectorIndexConfig": {
                "distance": "cosine"  # Cosine similarity for CLIP embeddings
            },
            "properties": [
                {
                    "name": "plantId",
                    "dataType": ["int"],
                    "description": "Unique identifier for the plant"
                },
                {
                    "name": "scientificName",
                    "dataType": ["text"],
                    "description": "Scientific name of the plant"
                },
                {
                    "name": "commonName",
                    "dataType": ["text"],
                    "description": "Common name of the plant"
                },
                {
                    "name": "family",
                    "dataType": ["text"],
                    "description": "Plant family (e.g., Rosaceae)"
                },
                {
                    "name": "imageUrl",
                    "dataType": ["text"],
                    "description": "URL or path to the plant image"
                },
                {
                    "name": "description",
                    "dataType": ["text"],
                    "description": "Detailed description of the plant"
                },
                {
                    "name": "createdAt",
                    "dataType": ["text"],
                    "description": "Timestamp when the entry was created"
                }
            ]
        }
        
        try:
            # Check if schema already exists
            schema_exists = self.client.schema.exists(self.class_name)
            
            if schema_exists and force_recreate:
                logger.info(f"Deleting existing schema: {self.class_name}")
                self.client.schema.delete_class(self.class_name)
                schema_exists = False
            
            if not schema_exists:
                logger.info(f"Creating schema: {self.class_name}")
                self.client.schema.create_class(schema)
                logger.info(f"Schema created successfully: {self.class_name}")
                return True
            else:
                logger.info(f"Schema already exists: {self.class_name}")
                return True
                
        except Exception as e:
            logger.error(f"Schema creation error: {e}", exc_info=True)
            raise WeaviateConnectionError(
                message="Failed to create Weaviate schema",
                details={"error": str(e), "class": self.class_name}
            )
    
    def add_plant_image(self, embedding: List[float], plant_id: int, 
                        scientific_name: str, common_name: str, image_url: str,
                        family: str = "", description: str = ""):
        """
        Add a plant image with its CLIP embedding to Weaviate.
        
        Args:
            embedding: 512-dim CLIP vector
            plant_id: Unique plant ID
            scientific_name: Scientific name (e.g., "Rosa gallica")
            common_name: Common name (e.g., "French Rose")
            image_url: Image URL or path
            family: Plant family (optional)
            description: Plant description (optional)
        
        Returns:
            UUID of created object or None on error
        """
        
        data = {
            "plantId": plant_id,
            "scientificName": scientific_name,
            "commonName": common_name,
            "family": family,
            "imageUrl": image_url,
            "description": description,
            "createdAt": datetime.now(UTC).isoformat()
        }
        
        try:
            uuid = self.client.data_object.create(
                data_object=data, 
                class_name=self.class_name, 
                vector=embedding
            )
            logger.info(f"Added plant image: {scientific_name} ({uuid})")
            return uuid
        except Exception as e:
            logger.error(f"Failed to add plant image: {e}", exc_info=True)
            raise WeaviateConnectionError(
                message="Failed to add plant image to Weaviate",
                details={
                    "error": str(e), 
                    "plant": scientific_name,
                    "plant_id": plant_id
                }
            )
    
    def similarity_search(self, query_embedding: List[float], limit: int = 5):
        """
        Vector similarity search using cosine distance.
        
        Args:
            query_embedding: 512-dim CLIP vector from query image
            limit: Number of results to return (default: 5)
        
        Returns:
            List of similar plants with metadata and certainty scores
            [
                {
                    "plantId": 1,
                    "scientificName": "Rosa gallica",
                    "commonName": "French Rose",
                    "family": "Rosaceae",
                    "imageUrl": "path/to/image.jpg",
                    "description": "...",
                    "_additional": {
                        "certainty": 0.9983,  # Cosine similarity (0-1)
                        "distance": 0.0034    # Cosine distance (0-2)
                    }
                }
            ]
        """
        try:
            result = (
                self.client.query
                .get(self.class_name, [
                    "plantId", 
                    "scientificName", 
                    "commonName", 
                    "family",
                    "imageUrl",
                    "description",
                    "createdAt"
                ])
                .with_near_vector({"vector": query_embedding})
                .with_limit(limit)
                .with_additional(["certainty", "distance"])
                .do()
            )
            
            if "data" in result and "Get" in result["data"]:
                items = result["data"]["Get"].get(self.class_name, [])
                logger.info(f"Similarity search found {len(items)} results")
                return items
            
            logger.warning("No results found in similarity search")
            return []
            
        except Exception as e:
            logger.error(f"Vector search error: {e}", exc_info=True)
            raise WeaviateConnectionError(
                message="Failed to perform similarity search",
                details={"error": str(e), "limit": limit}
            )
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get current schema information"""
        try:
            schema = self.client.schema.get(self.class_name)
            return schema
        except Exception as e:
            logger.error(f"Failed to get schema info: {e}")
            return {}
    
    def count_objects(self) -> int:
        """Count total objects in the collection"""
        try:
            result = self.client.query.aggregate(self.class_name).with_meta_count().do()
            count = result.get("data", {}).get("Aggregate", {}).get(self.class_name, [{}])[0].get("meta", {}).get("count", 0)
            return count
        except Exception as e:
            logger.error(f"Failed to count objects: {e}")
            return 0

weaviate_service = WeaviateService()
