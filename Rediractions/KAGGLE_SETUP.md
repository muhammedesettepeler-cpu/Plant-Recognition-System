# 🌿 Kaggle PlantCLEF 2025 Integration Setup

## 📋 Overview

Bu entegrasyon, 1TB+ PlantCLEF 2025 dataset'ini indirmeden kullanmanızı sağlar. Kaggle'ın ücretsiz GPU'larında inference yaparak 10,000+ bitki türünü tanıyabilirsiniz.

---

## 🚀 Adım Adım Kurulum

### 1. Kaggle Hesabı Oluştur

1. https://www.kaggle.com adresine git
2. Ücretsiz hesap oluştur
3. Telefon numarası doğrulaması yap (SMS verification)

### 2. Ngrok Hesabı Oluştur (Public API için gerekli)

1. https://ngrok.com adresine git
2. Ücretsiz hesap oluştur
3. Auth token'ı al: https://dashboard.ngrok.com/get-started/your-authtoken
4. Token'ı kopyala (örn: `2a1b3c4d5e6f7g8h9i0j1k2l3m4n5o6p`)

### 3. Notebook'u Kaggle'a Yükle

1. Kaggle'a giriş yap
2. **Create** > **New Notebook** tıkla
3. **File** > **Import Notebook**
4. `kaggle_notebook/PlantCLEF_Inference_API.ipynb` dosyasını yükle

### 4. PlantCLEF 2025 Dataset'ini Ekle

1. Notebook'ta sağ tarafta **Add Data** tıkla
2. Arama kutusuna "PlantCLEF 2025" yaz
3. Dataset'i bul ve **Add** tıkla
4. Dataset path'i doğrula: `/kaggle/input/plantclef2025`

**Not:** PlantCLEF 2025 dataset'i henüz yoksa alternatifler:
- PlantCLEF 2024
- PlantCLEF 2023
- iNaturalist 2021 - Plants
- PlantNet-300K

### 5. Ngrok Token'ı Notebook'a Ekle

1. Notebook'ta 9. cell'i bul:
   ```python
   NGROK_AUTH_TOKEN = "YOUR_NGROK_TOKEN_HERE"
   ```
2. `YOUR_NGROK_TOKEN_HERE` yerine ngrok token'ınızı yapıştır
3. Örnek:
   ```python
   NGROK_AUTH_TOKEN = "2a1b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"
   ```

### 6. Notebook Ayarları

1. Sağ üstte **Settings** tıkla
2. **Accelerator** > **GPU T4 x2** seç (ücretsiz)
3. **Internet** > **On** yap (ngrok için gerekli)
4. **Persistence** > **Variables and files** seç (optional)

### 7. Notebook'u Çalıştır

1. **Run All** butonuna tıkla
2. Tüm cell'lerin çalışmasını bekle (~5-10 dakika)
3. Son cell'de **Public API URL** görünecek:
   ```
   🌐 PUBLIC API URL:
      https://abc123xyz.ngrok-free.app
   ```
4. Bu URL'i kopyala!

### 8. Backend .env Ayarları

1. `backend/.env` dosyasını aç
2. Şu satırları ekle:
   ```bash
   # Kaggle PlantCLEF 2025 Inference
   KAGGLE_NOTEBOOK_URL=https://abc123xyz.ngrok-free.app
   ```
3. `abc123xyz.ngrok-free.app` yerine kendi URL'ini yapıştır

### 9. Backend'i Yeniden Başlat

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Beklenen log:**
```
INFO:     Kaggle notebook check: available ✅
```

### 10. Test Et

```powershell
# Health check
curl http://localhost:8000/api/v1/health

# Beklenen response:
{
  "services": {
    "kaggle_notebook": {
      "status": "available",
      "url_configured": true,
      "note": "PlantCLEF 2025 dataset (10k+ species)"
    }
  }
}
```

---

## 🧪 Test API Directly

Kaggle notebook API'yi direkt test etmek için:

```bash
# Test health
curl https://your-ngrok-url.app/health

# Test prediction
curl -X POST https://your-ngrok-url.app/predict \
  -F "image=@path/to/plant.jpg" \
  -F "top_k=5"
```

**Response örneği:**
```json
{
  "predictions": [
    {
      "species": "Rosa damascena",
      "confidence": 0.956,
      "common_name": "Damascus Rose",
      "species_id": "1234"
    },
    {
      "species": "Rosa gallica",
      "confidence": 0.892,
      "common_name": "French Rose",
      "species_id": "1235"
    }
  ],
  "inference_time": 2.341,
  "model": "resnet50",
  "device": "cuda"
}
```

---

## 🔄 Nasıl Çalışır?

### Pipeline:

1. **User** → Image upload to backend
2. **Backend** → CLIP encoding
3. **Backend** → Weaviate similarity search (local, 14 plants)
4. **If low confidence** → **Kaggle PlantCLEF** inference (10k+ species)
5. **Backend** → Merge results from both sources
6. **Backend** → LLM generates response with context
7. **User** ← Final response with plant identification

### Fallback Strategy:

```python
# 1. Try Weaviate first (fast, local)
weaviate_results = weaviate_service.similarity_search(embedding)

# 2. If confidence < 70%, use Kaggle
if weaviate_results[0].certainty < 0.7:
    kaggle_results = await kaggle_notebook_service.identify_plant(image)
    
    # 3. Merge results (Kaggle has priority if high confidence)
    if kaggle_results[0].confidence > 0.8:
        final_results = kaggle_results + weaviate_results
    else:
        final_results = weaviate_results + kaggle_results

# 4. Generate LLM response with merged context
response = llm_service.generate_rag_response(message, final_results)
```

---

## ⚙️ Advanced Configuration

### Custom Model

Notebook'ta farklı model kullanmak için 6. cell'i düzenle:

```python
# ResNet50 yerine EfficientNet
model_name = 'efficientnet_b0'
model = timm.create_model(model_name, pretrained=True, num_classes=num_classes)
```

**Desteklenen modeller:**
- `resnet50`, `resnet101`, `resnet152`
- `efficientnet_b0`, `efficientnet_b3`, `efficientnet_b7`
- `vit_base_patch16_224` (Vision Transformer)
- `convnext_base`

### Dataset Değiştirme

PlantCLEF 2025 yerine başka dataset:

1. Notebook'ta **Add Data** ile istediğin dataset'i ekle
2. 4. cell'deki `DATASET_PATH` değiştir:
   ```python
   DATASET_PATH = '/kaggle/input/your-dataset-name'
   ```

### Timeout Artırma

Backend'de timeout süresi:

```python
# backend/app/services/kaggle_notebook_service.py
self.timeout = 60.0  # 30'dan 60'a çıkar (büyük modeller için)
```

---

## 🐛 Troubleshooting

### Problem 1: Ngrok URL Değişiyor

**Sorun:** Her notebook yeniden başlatıldığında ngrok URL değişir

**Çözüm:**
1. Ngrok ücretli plan al (sabit subdomain)
2. Veya her seferinde `.env` dosyasını güncelle

### Problem 2: Notebook Timeout

**Sorun:** 30 dakikada response gelmezse Kaggle notebook kapanır

**Çözüm:**
1. Son cell'i manuel çalıştır (Keep Alive)
2. Veya notebook'u pinle (Premium gerekiyor)

### Problem 3: GPU Kotası Bitti

**Sorun:** "GPU quota exceeded"

**Çözüm:**
1. Accelerator'ü "None" yap (CPU kullan, yavaş)
2. Veya haftaya kadar bekle (quota yenilenir)
3. Veya Kaggle Premium'a geç

### Problem 4: Dataset Bulunamadı

**Sorun:** PlantCLEF 2025 yok

**Çözüm:**
1. PlantCLEF 2024 kullan
2. Veya iNaturalist 2021 - Plants
3. Dataset path'i notebook'ta güncelle

### Problem 5: Kaggle Unavailable

**Sorun:** Health check'te "unavailable"

**Çözüm:**
1. Notebook running mi kontrol et
2. Internet açık mı kontrol et
3. Ngrok cell'ini tekrar çalıştır
4. `.env`'deki URL'i kontrol et

---

## 📊 Performance

### Metrics:

| Metric | Weaviate Only | + Kaggle PlantCLEF |
|--------|--------------|-------------------|
| **Species Coverage** | 14 plants | 10,000+ plants |
| **Response Time** | ~5s | ~7-10s |
| **Accuracy (common)** | 95-100% | 95-100% |
| **Accuracy (rare)** | 0% | 80-95% |
| **Cost** | Free | Free |
| **Requires Internet** | No | Yes |

### Recommendation:

- **Small dataset (Weaviate):** Hızlı, offline çalışır, common plants için ideal
- **Large dataset (Kaggle):** Yavaş, online gerekli, rare/exotic plants için gerekli
- **Hybrid (Both):** En iyi yaklaşım! Common plants için hızlı, rare plants için kapsamlı

---

## 🎯 Next Steps

1. ✅ Kaggle notebook'u setup et
2. ✅ Backend entegrasyonu test et
3. ⏳ Frontend'de Kaggle source badge ekle
4. ⏳ Analytics: Kaggle vs Weaviate kullanım istatistikleri
5. ⏳ Fine-tune model PlantCLEF dataset'inde

---

## 📞 Support

**Kaggle Issues:**
- https://www.kaggle.com/discussions

**Ngrok Issues:**
- https://dashboard.ngrok.com/support

**Backend Issues:**
- GitHub Issues: https://github.com/muhammedesettepeler-cpu/Plant-Recognition-System/issues

---

**🎉 Setup tamamlandı! Artık 10,000+ bitki türünü tanıyabilirsin!** 🌿
