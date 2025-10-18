"""
Populate Weaviate with test plant data
Creates synthetic plant images and adds them to Weaviate for testing
"""
import sys
sys.path.insert(0, 'backend')

from app.services.weaviate_service import weaviate_service
from app.services.clip_service import clip_service
from PIL import Image, ImageDraw, ImageFont
import io

# Test plant data - real plant information
TEST_PLANTS = [
    {
        "id": 1,
        "scientific_name": "Rosa gallica",
        "common_name": "French Rose",
        "family": "Rosaceae",
        "color": (220, 20, 60),  # Crimson
        "description": "A species of rose native to southern and central Europe. Known for deep pink to red flowers."
    },
    {
        "id": 2,
        "scientific_name": "Rosa chinensis",
        "common_name": "China Rose",
        "family": "Rosaceae",
        "color": (255, 105, 180),  # Hot pink
        "description": "Native to Southwest China, known for repeat-flowering and disease resistance."
    },
    {
        "id": 3,
        "scientific_name": "Lavandula angustifolia",
        "common_name": "English Lavender",
        "family": "Lamiaceae",
        "color": (147, 112, 219),  # Medium purple
        "description": "Aromatic flowering plant native to Mediterranean. Used for essential oils and aromatherapy."
    },
    {
        "id": 4,
        "scientific_name": "Helianthus annuus",
        "common_name": "Sunflower",
        "family": "Asteraceae",
        "color": (255, 215, 0),  # Gold
        "description": "Large flowering plant native to Americas. Known for following the sun and edible seeds."
    },
    {
        "id": 5,
        "scientific_name": "Tulipa gesneriana",
        "common_name": "Garden Tulip",
        "family": "Liliaceae",
        "color": (255, 0, 0),  # Red
        "description": "Popular spring-blooming flower, native to Central Asia. Symbol of Netherlands."
    },
    {
        "id": 6,
        "scientific_name": "Viola tricolor",
        "common_name": "Pansy",
        "family": "Violaceae",
        "color": (138, 43, 226),  # Blue violet
        "description": "Small flowering plant with distinctive face-like markings. Edible flower."
    },
    {
        "id": 7,
        "scientific_name": "Narcissus pseudonarcissus",
        "common_name": "Daffodil",
        "family": "Amaryllidaceae",
        "color": (255, 255, 0),  # Yellow
        "description": "Spring-blooming perennial with trumpet-shaped flowers. National flower of Wales."
    },
    {
        "id": 8,
        "scientific_name": "Chrysanthemum morifolium",
        "common_name": "Chrysanthemum",
        "family": "Asteraceae",
        "color": (255, 140, 0),  # Dark orange
        "description": "Popular ornamental flowering plant. Symbol of autumn in many cultures."
    },
    {
        "id": 9,
        "scientific_name": "Iris germanica",
        "common_name": "German Iris",
        "family": "Iridaceae",
        "color": (75, 0, 130),  # Indigo
        "description": "Bearded iris with distinctive sword-like leaves. Popular garden flower."
    },
    {
        "id": 10,
        "scientific_name": "Bellis perennis",
        "common_name": "Common Daisy",
        "family": "Asteraceae",
        "color": (255, 255, 255),  # White
        "description": "Small white flowering plant common in European lawns. Symbol of innocence."
    },
]

def create_synthetic_plant_image(plant_data, size=(224, 224)):
    """
    Create a synthetic plant image with color representing the plant
    """
    # Create base image with plant color
    img = Image.new('RGB', size, color=plant_data['color'])
    
    # Add some variation to make images slightly different
    draw = ImageDraw.Draw(img)
    
    # Draw simple flower-like pattern
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # Draw center circle (darker)
    darker_color = tuple(max(0, c - 50) for c in plant_data['color'])
    draw.ellipse(
        [center_x - 30, center_y - 30, center_x + 30, center_y + 30],
        fill=darker_color
    )
    
    # Draw petals (lighter)
    lighter_color = tuple(min(255, c + 30) for c in plant_data['color'])
    for angle in range(0, 360, 45):
        import math
        rad = math.radians(angle)
        x = center_x + int(50 * math.cos(rad))
        y = center_y + int(50 * math.sin(rad))
        draw.ellipse(
            [x - 20, y - 20, x + 20, y + 20],
            fill=lighter_color
        )
    
    return img

def populate_weaviate():
    """
    Main function to populate Weaviate with test plant data
    """
    print("="*60)
    print("  POPULATING WEAVIATE WITH TEST PLANT DATA")
    print("="*60)
    
    # Step 1: Connect to Weaviate
    print("\n[1/4] Connecting to Weaviate Cloud...")
    try:
        weaviate_service.connect()
        print("     Connected successfully!")
    except Exception as e:
        print(f"     ERROR: {e}")
        return
    
    # Step 2: Ensure schema exists
    print("\n[2/4] Ensuring schema exists...")
    try:
        weaviate_service.create_schema(force_recreate=False)
        print("     Schema ready!")
    except Exception as e:
        print(f"     ERROR: {e}")
        return
    
    # Step 3: Load CLIP model
    print("\n[3/4] Loading CLIP model...")
    try:
        clip_service.load_model()
        print("     CLIP model loaded!")
    except Exception as e:
        print(f"     ERROR: {e}")
        return
    
    # Step 4: Add plants to Weaviate
    print(f"\n[4/4] Adding {len(TEST_PLANTS)} plants to Weaviate...")
    
    added_count = 0
    failed_count = 0
    
    for i, plant in enumerate(TEST_PLANTS, 1):
        try:
            print(f"\n  [{i}/{len(TEST_PLANTS)}] {plant['scientific_name']} ({plant['common_name']})")
            
            # Create synthetic image
            print(f"       Creating synthetic image...")
            img = create_synthetic_plant_image(plant)
            
            # Encode with CLIP
            print(f"       Encoding with CLIP...")
            embedding = clip_service.encode_image(img)
            
            if embedding is None or len(embedding) == 0:
                print(f"       ERROR: Failed to encode image")
                failed_count += 1
                continue
            
            # Add to Weaviate
            print(f"       Adding to Weaviate...")
            uuid = weaviate_service.add_plant_image(
                embedding=embedding,
                plant_id=plant['id'],
                scientific_name=plant['scientific_name'],
                common_name=plant['common_name'],
                family=plant['family'],
                image_url=f"synthetic/{plant['scientific_name'].lower().replace(' ', '_')}.jpg",
                description=plant['description']
            )
            
            print(f"       SUCCESS! UUID: {uuid[:8]}...")
            added_count += 1
            
        except Exception as e:
            print(f"       ERROR: {e}")
            failed_count += 1
            continue
    
    # Summary
    print("\n" + "="*60)
    print("  SUMMARY")
    print("="*60)
    print(f"  Total plants: {len(TEST_PLANTS)}")
    print(f"  Successfully added: {added_count}")
    print(f"  Failed: {failed_count}")
    
    # Verify count
    total_in_db = weaviate_service.count_objects()
    print(f"  Total objects in Weaviate: {total_in_db}")
    
    if added_count > 0:
        print("\n  SUCCESS! Test data populated.")
        print("  You can now test similarity search with plant images!")
    else:
        print("\n  FAILED! No data was added.")

if __name__ == "__main__":
    populate_weaviate()
