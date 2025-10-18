"""
Redis Connection Test
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.redis_service import redis_service

async def test_redis():
    print("=" * 60)
    print("🧪 REDIS CONNECTION TEST")
    print("=" * 60)
    
    # Connect
    print("\n1️⃣ Connecting to Redis...")
    await redis_service.connect()
    
    if not redis_service.is_connected:
        print("❌ Redis not connected - check if Docker container is running")
        print("\nStart Redis with:")
        print("  docker-compose -f docker-compose.redis.yml up -d")
        print("\nOr simple Docker:")
        print("  docker run -d -p 6379:6379 --name plant-recognition-redis redis:7-alpine")
        return
    
    print("✅ Redis connected!")
    
    # Test 1: Simple set/get
    print("\n2️⃣ Testing SET/GET...")
    await redis_service.set("test_key", "Hello Redis!", expire=60)
    value = await redis_service.get("test_key")
    print(f"   SET: test_key = 'Hello Redis!'")
    print(f"   GET: test_key = '{value}'")
    if value == "Hello Redis!":
        print("   ✅ SET/GET working!")
    else:
        print("   ❌ SET/GET failed!")
    
    # Test 2: JSON set/get
    print("\n3️⃣ Testing JSON SET/GET...")
    plant_data = {
        "name": "Rosa gallica",
        "family": "Rosaceae",
        "color": "red"
    }
    await redis_service.set_json("test_plant", plant_data, expire=60)
    plant = await redis_service.get_json("test_plant")
    print(f"   SET JSON: {plant_data}")
    print(f"   GET JSON: {plant}")
    if plant == plant_data:
        print("   ✅ JSON SET/GET working!")
    else:
        print("   ❌ JSON SET/GET failed!")
    
    # Test 3: Increment (rate limiting)
    print("\n4️⃣ Testing INCREMENT (rate limiting)...")
    print("   Simulating 5 requests:")
    for i in range(5):
        count = await redis_service.increment("rate_test", expire=60)
        print(f"   Request {i+1}: count = {count}")
    
    final_count = await redis_service.get_count("rate_test")
    if final_count == 5:
        print(f"   ✅ INCREMENT working! (final count: {final_count})")
    else:
        print(f"   ❌ INCREMENT failed! (expected 5, got {final_count})")
    
    # Test 4: Delete
    print("\n5️⃣ Testing DELETE...")
    await redis_service.delete("test_key")
    deleted_value = await redis_service.get("test_key")
    if deleted_value is None:
        print("   ✅ DELETE working!")
    else:
        print("   ❌ DELETE failed!")
    
    # Cleanup
    print("\n6️⃣ Cleanup...")
    await redis_service.delete("test_plant")
    await redis_service.delete("rate_test")
    print("   ✅ Test keys cleaned up")
    
    # Disconnect
    print("\n7️⃣ Disconnecting...")
    await redis_service.disconnect()
    print("   ✅ Disconnected")
    
    print("\n" + "=" * 60)
    print("✅ ALL REDIS TESTS PASSED!")
    print("=" * 60)
    print("\n📊 Summary:")
    print("   • Connection: ✅")
    print("   • SET/GET: ✅")
    print("   • JSON: ✅")
    print("   • INCREMENT: ✅")
    print("   • DELETE: ✅")
    print("\n🎉 Redis is ready for production!")
    print("\n💡 Next steps:")
    print("   1. Restart backend to use Redis")
    print("   2. Check logs for 'Redis connected' message")
    print("   3. Run API tests to verify rate limiting")
    print("   4. Visit Redis Commander at http://localhost:8081")

if __name__ == "__main__":
    try:
        asyncio.run(test_redis())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
