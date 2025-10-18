"""
Weaviate Cloud Connection Test
Tests connection, schema creation, and basic operations
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.services.weaviate_service import weaviate_service
from app.services.clip_service import clip_service
from PIL import Image
import numpy as np

def test_connection():
    """Test Weaviate Cloud connection"""
    print("\n🔄 Testing Weaviate Cloud connection...")
    try:
        connected = weaviate_service.connect()
        if connected:
            print("✅ Weaviate Cloud connected successfully!")
            return True
        else:
            print("❌ Failed to connect to Weaviate Cloud")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_schema_creation():
    """Test schema creation"""
    print("\n Creating schema...")
    try:
        # Check if schema already exists
        if weaviate_service.client.schema.exists(weaviate_service.class_name):
            print(f"⚠️  Schema '{weaviate_service.class_name}' already exists")
            print("   Deleting existing schema...")
            weaviate_service.client.schema.delete_class(weaviate_service.class_name)
        
        # Create new schema
        schema_created = weaviate_service.create_schema()
        if schema_created:
            print(f"✅ Schema '{weaviate_service.class_name}' created successfully!")
            
            # Verify schema
            schema = weaviate_service.client.schema.get(weaviate_service.class_name)
            print(f"   Properties: {len(schema.get('properties', []))}")
            for prop in schema.get('properties', []):
                print(f"      - {prop['name']}: {prop['dataType']}")
            return True
        else:
            print("❌ Failed to create schema")
            return False
    except Exception as e:
        print(f"❌ Schema creation error: {e}")
        return False

def test_add_data():
    """Test adding data with CLIP embeddings"""
    print("\n🔄 Testing data insertion...")
    try:
        # Create test images
        test_plants = [
            {
                "name": "Test Rose",
                "scientific": "Rosa damascena",
                "common": "Damascus Rose",
                "color": (255, 100, 100)  # Red-ish
            },
            {
                "name": "Test Sunflower",
                "scientific": "Helianthus annuus",
                "common": "Sunflower",
                "color": (255, 255, 0)  # Yellow
            },
            {
                "name": "Test Lavender",
                "scientific": "Lavandula angustifolia",
                "common": "English Lavender",
                "color": (200, 150, 255)  # Purple-ish
            }
        ]
        
        added_count = 0
        for i, plant in enumerate(test_plants):
            print(f"\n   Adding {plant['name']}...")
            
            # Create test image
            img = Image.new('RGB', (224, 224), color=plant['color'])
            
            # Encode with CLIP
            print("      Encoding with CLIP...")
            embedding = clip_service.encode_image(img)
            
            if embedding:
                print(f"      Embedding: {len(embedding)} dimensions")
                
                # Add to Weaviate
                result = weaviate_service.add_plant_image(
                    embedding=embedding,
                    plant_id=i + 1,
                    scientific_name=plant['scientific'],
                    common_name=plant['common'],
                    image_url=f"test_{plant['name'].lower().replace(' ', '_')}.jpg"
                )
                
                if result:
                    print(f"      ✅ Added successfully! ID: {result}")
                    added_count += 1
                else:
                    print("      ❌ Failed to add")
            else:
                print("      ❌ Failed to encode image")
        
        print(f"\n✅ Added {added_count}/{len(test_plants)} test plants")
        return added_count > 0
        
    except Exception as e:
        print(f"❌ Data insertion error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_similarity_search():
    """Test similarity search"""
    print("\n🔄 Testing similarity search...")
    try:
        # Create query image (red-ish like rose)
        query_img = Image.new('RGB', (224, 224), color=(255, 80, 80))
        
        print("   Encoding query image...")
        query_embedding = clip_service.encode_image(query_img)
        
        if not query_embedding:
            print("   ❌ Failed to encode query image")
            return False
        
        print(f"   Query embedding: {len(query_embedding)} dimensions")
        
        # Search
        print("   Searching for similar plants...")
        results = weaviate_service.similarity_search(query_embedding, limit=5)
        
        if results:
            print(f"\n✅ Found {len(results)} similar plants:")
            for i, result in enumerate(results, 1):
                certainty = result.get('_additional', {}).get('certainty', 0)
                scientific = result.get('scientificName', 'Unknown')
                common = result.get('commonName', 'Unknown')
                print(f"   {i}. {scientific} ({common})")
                print(f"      Similarity: {certainty:.4f}")
            return True
        else:
            print("   ⚠️  No results found")
            return False
            
    except Exception as e:
        print(f"❌ Similarity search error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_count():
    """Test counting objects in Weaviate"""
    print("\n🔄 Counting objects in Weaviate...")
    try:
        result = weaviate_service.client.query.aggregate(weaviate_service.class_name).with_meta_count().do()
        
        if 'data' in result and 'Aggregate' in result['data']:
            count = result['data']['Aggregate'][weaviate_service.class_name][0]['meta']['count']
            print(f"✅ Total objects: {count}")
            return True
        else:
            print("⚠️  Could not get count")
            return False
    except Exception as e:
        print(f"❌ Count error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🌿 Weaviate Cloud Test Suite")
    print("=" * 60)
    
    results = {
        "connection": False,
        "schema": False,
        "add_data": False,
        "search": False,
        "count": False
    }
    
    # Test 1: Connection
    results["connection"] = test_connection()
    if not results["connection"]:
        print("\n❌ Cannot proceed without connection")
        return
    
    # Test 2: Schema
    results["schema"] = test_schema_creation()
    if not results["schema"]:
        print("\n❌ Cannot proceed without schema")
        return
    
    # Test 3: Add data
    results["add_data"] = test_add_data()
    
    # Test 4: Count
    results["count"] = test_data_count()
    
    # Test 5: Search
    results["search"] = test_similarity_search()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name.replace('_', ' ').title()}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n🎯 Result: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! Weaviate is ready!")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")

if __name__ == "__main__":
    main()
