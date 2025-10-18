"""
Load Kaggle dataset into Weaviate vector database
Prepares CLIP embeddings for similarity search
"""
import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.kaggle_service import kaggle_service
from app.services.weaviate_service import weaviate_service
from app.services.clip_service import clip_service
from PIL import Image

async def load_kaggle_to_weaviate(limit: int = 1000):
    print(f"Loading Kaggle dataset to Weaviate (limit: {limit})")
    
    print("Fetching images from Kaggle...")
    images = kaggle_service.get_plant_images(limit=limit)
    print(f"Found {len(images)} images")
    
    print("Loading CLIP model...")
    await clip_service.load_model()
    
    print("Connecting to Weaviate...")
    await weaviate_service.connect()
    await weaviate_service.create_schema()
    
    print(f"Processing {len(images)} images...")
    success_count = 0
    error_count = 0
    
    for idx, image_path in enumerate(images, 1):
        try:
            image = Image.open(image_path)
            embedding = await clip_service.encode_image(image)
            
            plant_id = idx
            
            await weaviate_service.add_plant_image(
                plant_id=plant_id,
                image_url=image_path,
                embedding=embedding
            )
            
            success_count += 1
            
            if idx % 100 == 0:
                print(f"Progress: {idx}/{len(images)} ({success_count} success, {error_count} errors)")
        
        except Exception as e:
            error_count += 1
            print(f"Error ({image_path}): {str(e)}")
            continue
    
    print(f"\nLoading completed!")
    print(f"Success: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Success rate: {(success_count/len(images)*100):.2f}%")

if __name__ == "__main__":
    # Örnek: İlk 100 görseli yükle
    asyncio.run(load_kaggle_to_weaviate(limit=100))
