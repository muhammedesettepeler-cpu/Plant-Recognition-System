"""
USDA Plants Weaviate Import Script
Imports 93K plants from plantlst.txt to Weaviate Cloud
"""

import csv
import sys
import time
import logging
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.services.weaviate_service import weaviate_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# USDA Plants Schema for Weaviate (BM25 Keyword Search - Fast Import)
USDA_SCHEMA = {
    "class": "USDAPlant",
    "description": "USDA Plants Database - 93K plants for validation",
    "vectorizer": "none",  # No embeddings, use BM25 keyword search
    "properties": [
        {
            "name": "symbol",
            "dataType": ["text"],
            "description": "USDA plant symbol code",
        },
        {
            "name": "synonymSymbol",
            "dataType": ["text"],
            "description": "Synonym symbol",
        },
        {
            "name": "scientificName",
            "dataType": ["text"],
            "description": "Scientific name with author",
        },
        {
            "name": "commonName",
            "dataType": ["text"],
            "description": "Common English name",
        },
        {
            "name": "family",
            "dataType": ["text"],
            "description": "Plant family",
        },
    ],
}


def create_usda_schema(force_recreate: bool = False):
    """Create USDAPlant schema in Weaviate"""
    try:
        schema_exists = weaviate_service.client.schema.exists("USDAPlant")

        if schema_exists and force_recreate:
            logger.info("Deleting existing USDAPlant schema...")
            weaviate_service.client.schema.delete_class("USDAPlant")
            schema_exists = False

        if not schema_exists:
            logger.info("Creating USDAPlant schema...")
            weaviate_service.client.schema.create_class(USDA_SCHEMA)
            logger.info("✅ USDAPlant schema created")
            return True
        else:
            logger.info("USDAPlant schema already exists")
            return True

    except Exception as e:
        logger.error(f"Schema creation failed: {e}")
        return False


def import_usda_plants(file_path: str, batch_size: int = 100):
    """Import USDA plants in batches"""

    plants = []

    # Read CSV file
    logger.info(f"Reading {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header

        for row in reader:
            if len(row) >= 5:
                plants.append(
                    {
                        "symbol": row[0].strip(),
                        "synonymSymbol": row[1].strip(),
                        "scientificName": row[2].strip(),
                        "commonName": row[3].strip(),
                        "family": row[4].strip(),
                    }
                )

    logger.info(f"Loaded {len(plants)} plants from file")

    # Batch import
    total_imported = 0
    failed = 0
    start_time = time.time()

    logger.info("Starting batch import...")

    with weaviate_service.client.batch as batch:
        batch.batch_size = batch_size
        batch.dynamic = True

        for i, plant in enumerate(plants):
            try:
                batch.add_data_object(data_object=plant, class_name="USDAPlant")
                total_imported += 1

                # Progress log every 10k
                if (i + 1) % 10000 == 0:
                    elapsed = time.time() - start_time
                    rate = (i + 1) / elapsed
                    logger.info(
                        f"Progress: {i + 1}/{len(plants)} ({rate:.0f} plants/sec)"
                    )

            except Exception as e:
                failed += 1
                if failed <= 5:
                    logger.warning(
                        f"Failed to add plant: {plant['scientificName']}: {e}"
                    )

    elapsed = time.time() - start_time
    logger.info(f"✅ Import complete: {total_imported} plants in {elapsed:.1f}s")
    logger.info(f"   Rate: {total_imported / elapsed:.0f} plants/sec")
    if failed > 0:
        logger.warning(f"   Failed: {failed} plants")

    return total_imported


def verify_import():
    """Verify import by counting and sampling"""
    try:
        result = (
            weaviate_service.client.query.aggregate("USDAPlant").with_meta_count().do()
        )
        count = (
            result.get("data", {})
            .get("Aggregate", {})
            .get("USDAPlant", [{}])[0]
            .get("meta", {})
            .get("count", 0)
        )
        logger.info(f"Total plants in Weaviate: {count}")

        # Sample search
        sample = (
            weaviate_service.client.query.get(
                "USDAPlant", ["scientificName", "commonName", "family"]
            )
            .with_limit(3)
            .do()
        )

        if "data" in sample and "Get" in sample["data"]:
            plants = sample["data"]["Get"].get("USDAPlant", [])
            logger.info("Sample plants:")
            for p in plants:
                logger.info(
                    f"  - {p['scientificName']} ({p['commonName']}) - {p['family']}"
                )

        return count

    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return 0


def main():
    """Main import function"""
    print("=" * 60)
    print("🌿 USDA Plants Weaviate Import")
    print("=" * 60)

    # Connect to Weaviate
    logger.info("Connecting to Weaviate Cloud...")
    if not weaviate_service.connect():
        logger.error("❌ Failed to connect to Weaviate")
        return
    logger.info("✅ Connected to Weaviate")

    # Create schema
    if not create_usda_schema(force_recreate=True):
        logger.error("❌ Failed to create schema")
        return

    # Import plants
    file_path = Path(__file__).parent.parent.parent / "data" / "plantlst.txt"
    if not file_path.exists():
        logger.error(f"❌ File not found: {file_path}")
        return

    imported = import_usda_plants(str(file_path))

    # Verify
    print("\n" + "=" * 60)
    print("📊 Verification")
    print("=" * 60)
    verify_import()

    print("\n✅ USDA import complete!")


if __name__ == "__main__":
    main()
