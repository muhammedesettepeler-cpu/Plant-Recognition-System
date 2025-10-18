"""Quick search test"""
import sys
from pathlib import Path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.services.weaviate_service import weaviate_service
from app.services.clip_service import clip_service
from PIL import Image

print("🔄 Connecting to Weaviate...")
weaviate_service.connect()

print("\n🔄 Creating query image...")
query_img = Image.new('RGB', (224, 224), color=(255, 80, 80))

print("🔄 Encoding query...")
query_embedding = clip_service.encode_image(query_img)
print(f"   Embedding: {len(query_embedding)} dims")
print(f"   Sample values: {query_embedding[:5]}")

print("\n🔄 Searching...")
results = weaviate_service.similarity_search(query_embedding, limit=5)

if results:
    print(f"\n✅ Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result}")
else:
    print("❌ No results")
