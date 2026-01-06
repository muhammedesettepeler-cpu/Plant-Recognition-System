"""
USDA Plants Service - Weaviate Cloud Integration
Queries 93K plants from Weaviate Cloud for validation and enrichment
"""

import logging
from typing import Dict, List, Optional, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


class USDAPlantService:
    """
    Service for searching USDA Plants Database stored in Weaviate Cloud

    Data source: plantlst.txt (93,158 plants)
    Storage: Weaviate Cloud with text2vec vectorization
    """

    def __init__(self):
        self._weaviate_client = None
        self._class_name = "USDAPlant"

    def _get_client(self):
        """Lazy load Weaviate client"""
        if self._weaviate_client is None:
            try:
                from app.services.weaviate_service import weaviate_service

                if weaviate_service.client is None:
                    weaviate_service.connect()
                self._weaviate_client = weaviate_service.client
            except Exception as e:
                logger.error(f"Failed to get Weaviate client: {e}")
        return self._weaviate_client

    def find_by_scientific_name(self, scientific_name: str) -> Optional[Dict[str, str]]:
        """
        Find plant by scientific name using Weaviate text search

        Args:
            scientific_name: Scientific name to search (e.g., "Rosa damascena")

        Returns:
            Plant dict with symbol, scientificName, commonName, family
        """
        client = self._get_client()
        if not client:
            logger.warning("Weaviate client not available")
            return None

        try:
            # Extract base name (genus species) for better matching
            base_name = self._extract_base_name(scientific_name)

            # Use BM25 search for exact text matching
            result = (
                client.query.get(
                    self._class_name,
                    [
                        "symbol",
                        "synonymSymbol",
                        "scientificName",
                        "commonName",
                        "family",
                    ],
                )
                .with_bm25(query=base_name, properties=["scientificName"])
                .with_limit(1)
                .do()
            )

            if "data" in result and "Get" in result["data"]:
                plants = result["data"]["Get"].get(self._class_name, [])
                if plants:
                    plant = plants[0]
                    return {
                        "symbol": plant.get("symbol", ""),
                        "synonym_symbol": plant.get("synonymSymbol", ""),
                        "scientific_name": plant.get("scientificName", ""),
                        "common_name": plant.get("commonName", ""),
                        "family": plant.get("family", ""),
                    }

            return None

        except Exception as e:
            logger.error(f"USDA search error: {e}")
            return None

    def find_by_common_name(
        self, common_name: str, limit: int = 5
    ) -> List[Dict[str, str]]:
        """Find plants by common name"""
        client = self._get_client()
        if not client:
            return []

        try:
            result = (
                client.query.get(
                    self._class_name,
                    ["symbol", "scientificName", "commonName", "family"],
                )
                .with_bm25(query=common_name, properties=["commonName"])
                .with_limit(limit)
                .do()
            )

            if "data" in result and "Get" in result["data"]:
                plants = result["data"]["Get"].get(self._class_name, [])
                return [
                    {
                        "symbol": p.get("symbol", ""),
                        "scientific_name": p.get("scientificName", ""),
                        "common_name": p.get("commonName", ""),
                        "family": p.get("family", ""),
                    }
                    for p in plants
                ]

            return []

        except Exception as e:
            logger.error(f"USDA common name search error: {e}")
            return []

    def find_by_family(self, family: str, limit: int = 10) -> List[Dict[str, str]]:
        """Find plants by family name"""
        client = self._get_client()
        if not client:
            return []

        try:
            result = (
                client.query.get(
                    self._class_name,
                    ["symbol", "scientificName", "commonName", "family"],
                )
                .with_where(
                    {"path": ["family"], "operator": "Equal", "valueText": family}
                )
                .with_limit(limit)
                .do()
            )

            if "data" in result and "Get" in result["data"]:
                plants = result["data"]["Get"].get(self._class_name, [])
                return [
                    {
                        "symbol": p.get("symbol", ""),
                        "scientific_name": p.get("scientificName", ""),
                        "common_name": p.get("commonName", ""),
                        "family": p.get("family", ""),
                    }
                    for p in plants
                ]

            return []

        except Exception as e:
            logger.error(f"USDA family search error: {e}")
            return []

    def validate_plant(self, scientific_name: str) -> Dict[str, Any]:
        """
        Validate a plant name against USDA database

        Returns:
            Dict with validation result and additional info
        """
        plant = self.find_by_scientific_name(scientific_name)

        if plant:
            return {
                "valid": True,
                "usda_match": True,
                "scientific_name": plant["scientific_name"],
                "common_name": plant["common_name"],
                "family": plant["family"],
                "symbol": plant["symbol"],
                "source": "USDA Plants Database (Weaviate)",
            }
        else:
            return {
                "valid": False,
                "usda_match": False,
                "scientific_name": scientific_name,
                "message": "Not found in USDA Plants Database",
            }

    def enrich_plant_info(
        self, scientific_name: str, base_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enrich plant information with USDA data
        """
        usda_data = self.find_by_scientific_name(scientific_name)

        if usda_data:
            base_info["usda_verified"] = True
            base_info["usda_symbol"] = usda_data["symbol"]

            # Add missing info from USDA
            if not base_info.get("family"):
                base_info["family"] = usda_data["family"]
            if not base_info.get("common_name"):
                base_info["common_name"] = usda_data["common_name"]

            # Add USDA as source
            sources = base_info.get("sources", [])
            if "USDA" not in sources:
                sources.append("USDA")
            base_info["sources"] = sources
        else:
            base_info["usda_verified"] = False

        return base_info

    def _extract_base_name(self, full_name: str) -> str:
        """Extract genus species from full scientific name with author"""
        if not full_name:
            return ""

        parts = full_name.split()
        if len(parts) >= 2:
            return f"{parts[0]} {parts[1]}"
        return full_name

    def get_count(self) -> int:
        """Get total plant count from Weaviate"""
        client = self._get_client()
        if not client:
            return 0

        try:
            result = client.query.aggregate(self._class_name).with_meta_count().do()
            count = (
                result.get("data", {})
                .get("Aggregate", {})
                .get(self._class_name, [{}])[0]
                .get("meta", {})
                .get("count", 0)
            )
            return count
        except Exception as e:
            logger.error(f"Failed to get count: {e}")
            return 0

    @property
    def is_available(self) -> bool:
        """Check if USDA data is available in Weaviate"""
        return self.get_count() > 0


# Singleton instance
usda_service = USDAPlantService()
