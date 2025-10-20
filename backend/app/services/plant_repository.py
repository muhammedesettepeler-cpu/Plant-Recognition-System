"""
Plant Repository Service
Manages plant data persistence in PostgreSQL
"""
from sqlalchemy.orm import Session
from app.models.plant import Plant
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class PlantRepository:
    """Service for managing plant data in PostgreSQL"""
    
    @staticmethod
    def get_plant_by_scientific_name(db: Session, scientific_name: str) -> Optional[Plant]:
        """Get plant details from PostgreSQL by scientific name"""
        try:
            plant = db.query(Plant).filter(
                Plant.scientific_name == scientific_name
            ).first()
            return plant
        except Exception as e:
            logger.error(f"Error fetching plant {scientific_name}: {e}")
            return None
    
    @staticmethod
    def create_or_update_plant(db: Session, plant_data: Dict[str, Any]) -> Optional[Plant]:
        """
        Create new plant or update existing one with data from PlantNet/other sources
        
        plant_data should contain:
        - scientific_name (required)
        - scientific_name_full
        - common_names (list)
        - family
        - genus
        - description
        - habitat
        - care_instructions
        - characteristics (dict)
        - image_urls (list)
        - gbif_id
        - plantnet_verified
        """
        try:
            scientific_name = plant_data.get("scientific_name")
            if not scientific_name:
                logger.error("scientific_name is required")
                return None
            
            # Check if plant already exists
            plant = PlantRepository.get_plant_by_scientific_name(db, scientific_name)
            
            if plant:
                # Update existing plant
                logger.info(f"Updating existing plant: {scientific_name}")
                for key, value in plant_data.items():
                    if hasattr(plant, key) and value is not None:
                        setattr(plant, key, value)
            else:
                # Create new plant
                logger.info(f"Creating new plant: {scientific_name}")
                
                # Set primary common name from list
                common_names = plant_data.get("common_names", [])
                common_name = common_names[0] if common_names else None
                
                plant = Plant(
                    scientific_name=scientific_name,
                    scientific_name_full=plant_data.get("scientific_name_full"),
                    common_name=common_name,
                    common_names=common_names,
                    family=plant_data.get("family"),
                    genus=plant_data.get("genus"),
                    description=plant_data.get("description"),
                    habitat=plant_data.get("habitat"),
                    care_instructions=plant_data.get("care_instructions"),
                    characteristics=plant_data.get("characteristics"),
                    image_urls=plant_data.get("image_urls", []),
                    gbif_id=plant_data.get("gbif_id"),
                    plantnet_verified=plant_data.get("plantnet_verified", False)
                )
                db.add(plant)
            
            db.commit()
            db.refresh(plant)
            logger.info(f"✅ Plant saved: {scientific_name}")
            return plant
            
        except Exception as e:
            logger.error(f"Error creating/updating plant: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def enrich_plant_data_for_llm(plant: Plant) -> str:
        """
        Convert Plant model to rich text context for LLM
        Returns Turkish description with all available details
        """
        if not plant:
            return ""
        
        parts = []
        
        # Scientific and common names
        parts.append(f"**{plant.scientific_name}**")
        if plant.common_name:
            parts.append(f" ({plant.common_name})")
        parts.append("\n")
        
        # Family and genus
        if plant.family:
            parts.append(f"- Familya: {plant.family}\n")
        if plant.genus:
            parts.append(f"- Cins: {plant.genus}\n")
        
        # All common names
        if plant.common_names and len(plant.common_names) > 1:
            parts.append(f"- Diğer İsimler: {', '.join(plant.common_names)}\n")
        
        # Description
        if plant.description:
            parts.append(f"\n📝 Açıklama:\n{plant.description}\n")
        
        # Habitat
        if plant.habitat:
            parts.append(f"\n🌍 Yaşam Alanı:\n{plant.habitat}\n")
        
        # Care instructions
        if plant.care_instructions:
            parts.append(f"\n🌱 Bakım:\n{plant.care_instructions}\n")
        
        # Characteristics
        if plant.characteristics:
            parts.append(f"\n✨ Özellikler:\n")
            for key, value in plant.characteristics.items():
                parts.append(f"- {key}: {value}\n")
        
        return "".join(parts)

# Global instance
plant_repository = PlantRepository()
