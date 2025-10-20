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

# Test plant data - real plant information with detailed characteristics
TEST_PLANTS = [
    # ROSA (ROSE) SPECIES - Detailed characteristics
    {
        "id": 1,
        "scientific_name": "Rosa gallica",
        "common_name": "French Rose / Fransız Gülü",
        "family": "Rosaceae",
        "color": (220, 20, 60),  # Crimson
        "description": "A species of rose native to southern and central Europe. Known for deep pink to red flowers. Leaves: Pinnately compound with 5-7 leaflets, serrated edges, dark green. Flowers: 5-petaled, fragrant, 4-6cm diameter. Height: 60-120cm. Blooming: Late spring to early summer. Soil: Well-drained, slightly acidic to neutral pH. Sunlight: Full sun to partial shade. Uses: Ornamental, perfume, rose water, herbal medicine."
    },
    {
        "id": 2,
        "scientific_name": "Rosa chinensis",
        "common_name": "China Rose / Çin Gülü",
        "family": "Rosaceae",
        "color": (255, 105, 180),  # Hot pink
        "description": "Native to Southwest China, known for repeat-flowering and disease resistance. Leaves: Compound with 3-5 glossy leaflets, oval shape. Flowers: Single or double, 5-10cm diameter, colors range from white to pink and red. Height: 90-180cm. Blooming: Repeat bloomer (spring to fall). Soil: Fertile, well-drained. Sunlight: Full sun. Special: Heat tolerant, used in tea production."
    },
    {
        "id": 3,
        "scientific_name": "Rosa damascena",
        "common_name": "Damask Rose / Şam Gülü",
        "family": "Rosaceae",
        "color": (255, 182, 193),  # Light pink
        "description": "Ancient rose cultivar, prized for essential oil production. Leaves: Compound with 5-7 downy, grey-green leaflets. Flowers: Very fragrant, double petals, 6-8cm diameter, pink to light red. Height: 120-180cm. Blooming: Summer flowering. Soil: Well-drained, loamy. Sunlight: Full sun. Uses: Rose oil (attar of roses), rosewater, cosmetics, culinary. Aroma: Intensely sweet and floral."
    },
    {
        "id": 4,
        "scientific_name": "Rosa canina",
        "common_name": "Dog Rose / Kuşburnu",
        "family": "Rosaceae",
        "color": (255, 192, 203),  # Pink
        "description": "Wild rose species native to Europe, northwest Africa and western Asia. Leaves: Compound with 5-7 leaflets, serrated. Flowers: 5 petals, pale pink to white, 4-5cm diameter. Height: 1-5m (climbing shrub). Blooming: Early summer. Fruits: Bright red rose hips (high in vitamin C). Soil: Adaptable. Sunlight: Full sun to partial shade. Uses: Medicinal (rose hip tea), hedges, rootstock for grafting."
    },
    
    # TULIPA (TULIP) SPECIES - Detailed characteristics
    {
        "id": 5,
        "scientific_name": "Tulipa gesneriana",
        "common_name": "Garden Tulip / Bahçe Lalesi",
        "family": "Liliaceae",
        "color": (255, 0, 0),  # Red
        "description": "Popular spring-blooming flower, native to Central Asia. Symbol of Netherlands. Leaves: 2-6 broad, lance-shaped, waxy, bluish-green, arranged in rosette. Flowers: Single cup-shaped, 6 petals, 5-10cm tall, colors include red, yellow, pink, white, purple, multicolor. Height: 25-60cm. Blooming: Early to mid spring. Bulb: Underground storage organ. Soil: Well-drained, fertile, neutral to slightly alkaline. Sunlight: Full sun to light shade."
    },
    {
        "id": 6,
        "scientific_name": "Tulipa acuminata",
        "common_name": "Horned Tulip / Boynuzlu Lale",
        "family": "Liliaceae",
        "color": (255, 215, 0),  # Gold/yellow
        "description": "Distinctive tulip with narrow, twisted, elongated petals. Leaves: 3-5 linear, waxy leaves. Flowers: Unique spider-like appearance, 6 narrow pointed petals (10-15cm long), twisted and curled, yellow with red streaks. Height: 40-50cm. Blooming: Mid to late spring. Soil: Well-drained. Sunlight: Full sun. Special: Very rare, ornamental conversation piece."
    },
    {
        "id": 7,
        "scientific_name": "Tulipa clusiana",
        "common_name": "Lady Tulip / Kadın Lalesi",
        "family": "Liliaceae",
        "color": (255, 255, 255),  # White and red
        "description": "Delicate species tulip from Iran and Afghanistan. Leaves: 3-4 narrow, linear, grey-green leaves. Flowers: Star-shaped when open, white petals with crimson-red exterior, yellow center, 4-5cm tall. Height: 20-30cm. Blooming: Early to mid spring. Soil: Well-drained, rocky. Sunlight: Full sun. Special: Naturalizes well, heat tolerant, perennial."
    },
    {
        "id": 8,
        "scientific_name": "Tulipa humilis",
        "common_name": "Dwarf Tulip / Cüce Lale",
        "family": "Liliaceae",
        "color": (255, 0, 255),  # Magenta
        "description": "Small species tulip native to Turkey and Iran. Leaves: 2-3 narrow, channeled leaves, grey-green. Flowers: Star-shaped, 6 petals, magenta-pink with yellow center, 3-4cm tall. Height: 10-15cm. Blooming: Early spring (February-March). Soil: Well-drained, gritty. Sunlight: Full sun. Special: Rock gardens, alpine troughs, very cold hardy (to -20°C)."
    },
    
    # OTHER POPULAR FLOWERS
    {
        "id": 9,
        "scientific_name": "Lavandula angustifolia",
        "common_name": "English Lavender / İngiliz Lavantası",
        "family": "Lamiaceae",
        "color": (147, 112, 219),  # Medium purple
        "description": "Aromatic flowering plant native to Mediterranean. Used for essential oils and aromatherapy. Leaves: Linear to lance-shaped, grey-green, opposite arrangement, 2-6cm long. Flowers: Small tubular, purple-blue, arranged in dense spikes, highly fragrant. Height: 30-60cm. Blooming: Mid to late summer. Soil: Well-drained, alkaline, dry. Sunlight: Full sun. Uses: Essential oil, potpourri, culinary, medicinal (calming effect)."
    },
    {
        "id": 10,
        "scientific_name": "Helianthus annuus",
        "common_name": "Sunflower / Ayçiçeği",
        "family": "Asteraceae",
        "color": (255, 215, 0),  # Gold
        "description": "Large flowering plant native to Americas. Known for following the sun (heliotropism) and edible seeds. Leaves: Large, heart-shaped, alternate, rough texture, 10-40cm long. Flowers: Large composite head (10-40cm diameter), yellow ray florets, brown central disc florets. Height: 1-4m. Blooming: Summer to early fall. Seeds: Black or striped, oil-rich. Soil: Well-drained, tolerant. Sunlight: Full sun. Uses: Seeds (food, oil), ornamental, bird feed."
    },
    {
        "id": 11,
        "scientific_name": "Viola tricolor",
        "common_name": "Pansy / Hercai Menekşe",
        "family": "Violaceae",
        "color": (138, 43, 226),  # Blue violet
        "description": "Small flowering plant with distinctive face-like markings. Edible flower. Leaves: Rounded to heart-shaped, scalloped edges, 2-4cm. Flowers: 5 petals, tricolor (purple, yellow, white), 2-3cm diameter, bilateral symmetry. Height: 10-20cm. Blooming: Spring to fall. Soil: Moist, well-drained, fertile. Sunlight: Partial shade to full sun. Uses: Ornamental, edible garnish, herbal medicine (anti-inflammatory)."
    },
    {
        "id": 12,
        "scientific_name": "Narcissus pseudonarcissus",
        "common_name": "Daffodil / Nergis",
        "family": "Amaryllidaceae",
        "color": (255, 255, 0),  # Yellow
        "description": "Spring-blooming perennial with trumpet-shaped flowers. National flower of Wales. Leaves: Strap-shaped, linear, 15-45cm long, bluish-green. Flowers: 6 petal-like tepals, central trumpet corona, yellow or white, 5-8cm diameter, fragrant. Height: 20-50cm. Blooming: Early spring. Bulb: Underground. Soil: Well-drained, moist. Sunlight: Full sun to partial shade. Special: Toxic if ingested, naturalizes well."
    },
    {
        "id": 13,
        "scientific_name": "Chrysanthemum morifolium",
        "common_name": "Chrysanthemum / Kasımpatı",
        "family": "Asteraceae",
        "color": (255, 140, 0),  # Dark orange
        "description": "Popular ornamental flowering plant. Symbol of autumn in many cultures. Leaves: Lobed, serrated edges, aromatic, 5-10cm long. Flowers: Composite head, various forms (single, double, pompom, spider), colors include white, yellow, pink, red, purple, 2-15cm diameter. Height: 30-90cm. Blooming: Late summer to fall. Soil: Well-drained, fertile. Sunlight: Full sun. Uses: Ornamental, chrysanthemum tea, traditional medicine."
    },
    {
        "id": 14,
        "scientific_name": "Iris germanica",
        "common_name": "German Iris / Alman Süseni",
        "family": "Iridaceae",
        "color": (75, 0, 130),  # Indigo
        "description": "Bearded iris with distinctive sword-like leaves. Popular garden flower. Leaves: Sword-shaped, flat, upright, grey-green, 30-90cm long. Flowers: 3 upright petals (standards), 3 drooping petals (falls) with fuzzy beard, fragrant, purple, blue, white, yellow, bicolor, 10-15cm diameter. Height: 60-90cm. Blooming: Late spring to early summer. Rhizome: Thick horizontal stem. Soil: Well-drained, neutral to slightly alkaline. Sunlight: Full sun."
    },
    {
        "id": 15,
        "scientific_name": "Bellis perennis",
        "common_name": "Common Daisy / Papatya",
        "family": "Asteraceae",
        "color": (255, 255, 255),  # White
        "description": "Small white flowering plant common in European lawns. Symbol of innocence. Leaves: Rosette of spoon-shaped leaves, 2-5cm long, slightly hairy. Flowers: Composite head, white ray florets, yellow central disc, 2-3cm diameter, closes at night. Height: 5-15cm. Blooming: Spring to fall. Soil: Adaptable, prefers moist. Sunlight: Full sun to partial shade. Uses: Ornamental, edible (salads), herbal medicine (wound healing)."
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
