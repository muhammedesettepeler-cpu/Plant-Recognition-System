"""
Initialize database - Create all tables
"""
import sys
sys.path.insert(0, 'backend')

from app.db.base import engine, Base
from app.models.plant import Plant, UserQuery
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Create all tables in the database"""
    logger.info("="*60)
    logger.info("  INITIALIZING DATABASE")
    logger.info("="*60)
    
    try:
        logger.info("\n Creating tables...")
        Base.metadata.create_all(bind=engine)
        logger.info(" All tables created successfully!")
        
        logger.info("\n Tables in database:")
        for table_name in Base.metadata.tables.keys():
            logger.info(f"  - {table_name}")
        
        logger.info("\nDatabase initialization complete!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    init_db()
