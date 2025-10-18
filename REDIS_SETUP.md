# 🚀 Redis Setup Guide (Docker)

## 📋 Gereksinimler
- Docker Desktop (Windows için)
- Download: https://www.docker.com/products/docker-desktop/

---

## 🐳 Adım 1: Redis Container Başlatma

### Basit Kurulum (Sadece Redis)
```powershell
# Redis container'ı başlat
docker run -d `
  --name plant-recognition-redis `
  -p 6379:6379 `
  redis:7-alpine

# Test et
docker exec -it plant-recognition-redis redis-cli ping
# Beklenen çıktı: PONG
```

### Tam Kurulum (Redis + Web UI)
```powershell
# Docker Compose ile başlat
docker-compose -f docker-compose.redis.yml up -d

# Log'ları kontrol et
docker-compose -f docker-compose.redis.yml logs -f

# Servisleri kontrol et
docker-compose -f docker-compose.redis.yml ps
```

**Servisler:**
- Redis: `localhost:6379`
- Redis Commander (Web UI): `http://localhost:8081`

---

## ⚙️ Adım 2: .env Ayarları

Backend `.env` dosyasına ekle:

```bash
# Redis (Docker)
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=
REDIS_DB=0
```

---

## 📦 Adım 3: Python Paketleri

```powershell
cd backend
..\.venv\Scripts\pip.exe install redis fastapi-limiter
```

Veya:

```powershell
cd backend
..\.venv\Scripts\pip.exe install -r requirements.txt
```

---

## ✅ Adım 4: Test

### 4.1 Redis Bağlantısı Test
```powershell
# Backend'i başlat
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Beklenen log:**
```
Connecting to Redis...
✅ Redis connected - using distributed cache
```

### 4.2 Redis CLI ile Test
```powershell
# Container içine gir
docker exec -it plant-recognition-redis redis-cli

# Redis komutları
> PING
PONG

> SET test "Hello Redis"
OK

> GET test
"Hello Redis"

> KEYS *
1) "test"

> DEL test
(integer) 1

> EXIT
```

### 4.3 Python ile Test
```python
# Test script: backend/test_redis.py
import asyncio
from app.services.redis_service import redis_service

async def test():
    await redis_service.connect()
    
    # Test set/get
    await redis_service.set("test_key", "test_value")
    value = await redis_service.get("test_key")
    print(f"Value: {value}")
    
    # Test JSON
    await redis_service.set_json("plant", {"name": "Rose", "family": "Rosaceae"})
    plant = await redis_service.get_json("plant")
    print(f"Plant: {plant}")
    
    # Test rate limiting
    for i in range(5):
        count = await redis_service.increment("rate_test", expire=60)
        print(f"Request {i+1}: count={count}")
    
    await redis_service.disconnect()

asyncio.run(test())
```

Çalıştır:
```powershell
cd backend
..\.venv\Scripts\python.exe test_redis.py
```

---

## 🎨 Redis Commander Web UI

Redis Commander'a tarayıcıdan eriş:
- URL: `http://localhost:8081`
- Server: `local` (otomatik bağlanır)

**Özellikler:**
- Tüm key'leri görüntüle
- Value'ları düzenle
- TTL (expire time) yönet
- Memory kullanımını izle
- Real-time monitoring

---

## 🔧 Docker Komutları

### Başlatma/Durdurma
```powershell
# Başlat
docker-compose -f docker-compose.redis.yml up -d

# Durdur
docker-compose -f docker-compose.redis.yml down

# Yeniden başlat
docker-compose -f docker-compose.redis.yml restart

# Log'ları göster
docker-compose -f docker-compose.redis.yml logs -f redis
```

### Durum Kontrolü
```powershell
# Container'ları listele
docker ps

# Redis stats
docker stats plant-recognition-redis

# Redis info
docker exec plant-recognition-redis redis-cli INFO
```

### Veri Temizleme
```powershell
# Tüm cache'i temizle
docker exec plant-recognition-redis redis-cli FLUSHALL

# Sadece DB 0'ı temizle
docker exec plant-recognition-redis redis-cli FLUSHDB
```

### Volume Temizleme (Dikkatli!)
```powershell
# Container'ı durdur ve verileri sil
docker-compose -f docker-compose.redis.yml down -v
```

---

## 📊 Monitoring & Debugging

### Redis CLI Monitoring
```powershell
# Real-time komutları izle
docker exec -it plant-recognition-redis redis-cli MONITOR

# Memory kullanımı
docker exec plant-recognition-redis redis-cli INFO memory

# Key sayısı
docker exec plant-recognition-redis redis-cli DBSIZE

# Slow log
docker exec plant-recognition-redis redis-cli SLOWLOG GET 10
```

### Backend Logs
```powershell
# Backend loglarında Redis aktivitesini izle
# main.py'da logging enabled olmalı
```

---

## 🚨 Troubleshooting

### Problem 1: Connection Refused
```
Error: Redis connection failed: Connection refused
```

**Çözüm:**
```powershell
# Container çalışıyor mu?
docker ps | findstr redis

# Port açık mı?
netstat -an | findstr 6379

# Container'ı yeniden başlat
docker restart plant-recognition-redis
```

### Problem 2: Container Başlamıyor
```powershell
# Logları kontrol et
docker logs plant-recognition-redis

# Port conflict?
docker port plant-recognition-redis
```

### Problem 3: Permission Denied
```powershell
# Windows'ta Docker Desktop'ı admin olarak çalıştır
# WSL2 backend kullanıyorsan WSL'i yeniden başlat
wsl --shutdown
```

---

## 🎯 Production Notları

### Güvenlik
```yaml
# docker-compose.redis.yml - Production için
command: redis-server --appendonly yes --requirepass "güçlü_şifre_buraya"
```

.env:
```bash
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=güçlü_şifre_buraya
```

### Performance
```yaml
# Daha fazla memory
command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

### Persistence
```yaml
volumes:
  - redis_data:/data
  - ./redis.conf:/usr/local/etc/redis/redis.conf
command: redis-server /usr/local/etc/redis/redis.conf
```

---

## 📝 Kullanım Örnekleri

### 1. Rate Limiting
```python
from fastapi import Depends
from app.core.rate_limiter import rate_limiter

@app.post("/chat", dependencies=[Depends(rate_limiter)])
async def chat(request: Request):
    # 10 requests/minute limit (Redis ile distributed)
    pass
```

### 2. Response Caching
```python
from app.services.redis_service import redis_service

cache_key = f"plant:{plant_id}"
cached = await redis_service.get_json(cache_key)
if cached:
    return cached

# Fetch from DB
result = await db.query(...)
await redis_service.set_json(cache_key, result, expire=3600)
```

### 3. Image Similarity Cache
```python
import hashlib

image_hash = hashlib.sha256(image_bytes).hexdigest()[:16]
cache_key = f"similarity:{image_hash}"

cached = await redis_service.get_json(cache_key)
if cached:
    return cached  # Skip expensive CLIP encoding

# Compute similarity
results = await weaviate_service.similarity_search(embedding)
await redis_service.set_json(cache_key, results, expire=86400)
```

---

## ✅ Checklist

- [ ] Docker Desktop kurulu
- [ ] `docker-compose.redis.yml` oluşturuldu
- [ ] Redis container başlatıldı (`docker-compose up -d`)
- [ ] Redis PING testi başarılı
- [ ] `.env` dosyasına REDIS_URL eklendi
- [ ] Python paketleri kuruldu (`redis`, `fastapi-limiter`)
- [ ] Backend başlatıldı ve Redis'e bağlandı
- [ ] Redis Commander'a erişildi (`localhost:8081`)
- [ ] Test script çalıştırıldı
- [ ] API testleri rate limiting ile geçti

---

## 🎉 Başarı Kriterleri

Backend başlatıldığında şu logları görmeli:

```
INFO:     Starting application initialization...
INFO:     Connecting to Redis...
INFO:     ✅ Redis connected - using distributed cache
INFO:     Loading CLIP model...
INFO:     CLIP model loaded successfully
INFO:     Connecting to Weaviate Cloud...
INFO:     Weaviate connection established
INFO:     Application initialization completed
```

Health check:
```json
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "weaviate": "healthy",
    "clip": "loaded",
    "redis": "connected"  // YENİ!
  }
}
```

---

**Hazır! Redis artık production-ready! 🚀**
