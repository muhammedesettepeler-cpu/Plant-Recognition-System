"""
Drop and recreate plants table with new schema
"""
import sys
sys.path.insert(0, 'backend')

from app.db.base import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_plants_table():
    """Drop and recreate plants table"""
    logger.info("="*60)
    logger.info("  RESETTING PLANTS TABLE")
    logger.info("="*60)
    
    try:
        with engine.connect() as conn:
            # Drop existing table
            logger.info("\n🗑️  Dropping existing plants table...")
            conn.execute(text("DROP TABLE IF EXISTS plants CASCADE"))
            conn.commit()
            logger.info("✅ Table dropped!")
            
            # Recreate with new schema
            logger.info("\n📊 Creating plants table with new schema...")
            conn.execute(text("""
                CREATE TABLE plants (
                    id SERIAL PRIMARY KEY,
                    scientific_name VARCHAR(255) UNIQUE NOT NULL,
                    scientific_name_full VARCHAR(300),
                    common_name VARCHAR(255),
                    common_names JSONB,
                    family VARCHAR(100),
                    genus VARCHAR(100),
                    description TEXT,
                    habitat TEXT,
                    care_instructions TEXT,
                    characteristics JSONB,
                    image_urls JSONB,
                    weaviate_id VARCHAR(255),
                    gbif_id VARCHAR(100),
                    plantnet_verified BOOLEAN DEFAULT FALSE,
                    last_updated TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
            logger.info("✅ Plants table created with new schema!")
            
            # Create indexes
            logger.info("\n📇 Creating indexes...")
            conn.execute(text("CREATE INDEX idx_plants_scientific_name ON plants(scientific_name)"))
            conn.execute(text("CREATE INDEX idx_plants_family ON plants(family)"))
            conn.commit()
            logger.info("✅ Indexes created!")
            
        logger.info("\n✨ Table reset complete!")
        
    except Exception as e:
        logger.error(f"❌ Reset failed: {e}")
        raise

if __name__ == "__main__":
    reset_plants_table()
