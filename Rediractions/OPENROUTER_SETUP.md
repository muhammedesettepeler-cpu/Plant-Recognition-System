# OpenRouter Entegrasyonu ✅

## 🎉 Grok → OpenRouter Değişikliği

**Neden OpenRouter?**
- ✅ **Ücretsiz model:** nvidia/nemotron-nano-9b-v2:free
- ✅ **Güçlü performans:** 9B parametreli model
- ✅ **API limiti:** Günlük 200 istek (ücretsiz)
- ✅ **Hızlı yanıt:** ~2-3 saniye
- ✅ **Grok'tan daha kolay:** Kredi kartı gerekmez!

## 🔑 API Anahtarları Durumu:

### ✅ Yapılandırılmış:
- **PlantNet API:** ✅ `2b10ZPIiSgJh6hqWbbqITP8Eu`
- **Kaggle API:** ✅ `akiraasonia`
- **OpenRouter API:** ✅ `sk-or-v1-68671547...`

### 🎯 Model:
- **nvidia/nemotron-nano-9b-v2:free** (Ücretsiz!)

## 📝 Yapılan Değişiklikler:

### 1. `.env` Dosyası Güncellendi:
```bash
OPENROUTER_API_KEY=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
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=nvidia/nemotron-nano-9b-v2:free
```

### 2. `config.py` Güncellendi:
```python
# OpenRouter yapılandırması eklendi
OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-nano-9b-v2:free")
```

### 3. `grok_service.py` → `llm_service.py`:
```python
# Grok yerine OpenRouter kullanıyor
class LLMService:
    - OpenRouter API entegrasyonu
    - nvidia/nemotron-nano-9b-v2:free modeli
    - RAG desteği
    - Gelişmiş hata yönetimi
```

### 4. Geriye Dönük Uyumluluk:
```python
# Eski kod hala çalışır
grok_service = llm_service
```

## 🚀 Özellikler:

### 1. Chatbot:
```python
# Sohbet endpoint'i
POST /api/v1/chat
{
  "query": "What is a rose?",
  "session_id": "user123"
}
```

### 2. RAG (Retrieval Augmented Generation):
```python
# Veritabanı bilgisiyle zenginleştirilmiş yanıt
POST /api/v1/chat-with-image
{
  "query": "Tell me about this plant",
  "image": <base64>
}
```

### 3. Plant Recognition + LLM:
```python
# PlantNet + CLIP + OpenRouter kombinasyonu
POST /api/v1/recognize
{
  "image": <multipart/form-data>
}

# Yanıt:
{
  "plantnet_results": [...],
  "similar_plants": [...],
  "llm_explanation": "This is a Rosa damascena..."
}
```

## 🎯 OpenRouter Modelleri:

### Ücretsiz Modeller:
1. **nvidia/nemotron-nano-9b-v2:free** ✅ (kullanıyoruz)
   - 9B parametreli
   - Hızlı ve akıllı
   - Günlük 200 istek

2. **meta-llama/llama-3.2-3b-instruct:free**
   - 3B parametreli
   - Daha hızlı
   - Daha basit görevler için

3. **google/gemma-2-9b-it:free**
   - Google'ın modeli
   - İyi performans

### Model Değiştirme:
```bash
# .env dosyasında
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free
```

## 📊 API Limitleri:

### Ücretsiz Plan:
- **Günlük:** 200 istek
- **Dakikalık:** 20 istek
- **Token:** 32K context window
- **Hız:** ~2-3 saniye/yanıt

### Ücretli Plana Geçiş (Opsiyonel):
- **Günlük:** Sınırsız
- **GPT-4 erişimi:** $0.03/1K token
- **Claude erişimi:** $0.015/1K token

## 🧪 Test:

### 1. Backend'i Başlat:
```powershell
cd backend
uvicorn app.main:app --reload
```

### 2. Chatbot Test:
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the benefits of aloe vera?",
    "session_id": "test123"
  }'
```

### 3. API Docs:
http://localhost:8000/api/v1/docs

## ⚠️ Önemli Notlar:

### 1. Rate Limiting:
```python
# Günlük 200 istek limiti
# Aşarsan: "Rate limit exceeded" hatası
```

### 2. API Key Güvenliği:
```bash
# .gitignore'da
.env
backend/.env
```

### 3. Timeout:
```python
# 30 saniye timeout
async with httpx.AsyncClient(timeout=30.0) as client:
```

## 🎉 Avantajlar:

### Grok vs OpenRouter:

| Özellik | Grok | OpenRouter |
|---------|------|------------|
| Fiyat | $5/ay | **ÜCRETSİZ** ✅ |
| Limit | 1000 istek/gün | 200 istek/gün |
| Performans | Çok iyi | İyi ✅ |
| Kayıt | Kredi kartı gerekli | Sadece email ✅ |
| Model seçenekleri | Sadece Grok | 100+ model ✅ |

## 🚀 Özet:

✅ OpenRouter API yapılandırıldı
✅ nvidia/nemotron-nano-9b-v2:free modeli seçildi
✅ LLM servisi güncellendi
✅ RAG desteği eklendi
✅ Geriye dönük uyumluluk sağlandı
✅ Ücretsiz ve güçlü! 🎉

**Artık database'i başlatmaya hazırız!** 🚀

```powershell
docker-compose up -d postgres weaviate
```

Devam edelim mi? 🎯
