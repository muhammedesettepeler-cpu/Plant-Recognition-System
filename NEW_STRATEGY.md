# 🔄 Güncellenmiş Proje Stratejisi

**Tarih**: 18 Ekim 2025  
**Değişiklik**: Kaggle Notebook yaklaşımına geçiş

---

## ❌ Eski Yaklaşım (İptal Edildi)

### Sorunlar
1. **Dataset Boyutu**: PlantCLEF 2025 ~1TB (indirme+saklama)
2. **Storage**: IDrive2 gerekiyordu
3. **İşlem Gücü**: Lokal GPU gerekli
4. **Maliyet**: Storage + compute

### İptal Edilen Bileşenler
- ❌ `backend/scripts/download_kaggle_data.py` (kullanılmayacak)
- ❌ `backend/scripts/load_kaggle_to_weaviate.py` (kullanılmayacak)
- ❌ IDrive2 entegrasyonu
- ❌ Lokal dataset storage
- ❌ Tüm PlantCLEF görsellerini Weaviate'e yükleme

---

## ✅ Yeni Yaklaşım (Kaggle Notebooks)

### Avantajlar
1. **✅ Veri Lokal Değil**: Dataset Kaggle'da kalıyor (1TB indirme yok)
2. **✅ Ücretsiz GPU**: Kaggle'ın GPU'larını kullanıyoruz
3. **✅ Storage Yok**: IDrive2 gereksiz
4. **✅ Güncel Veri**: PlantCLEF güncellemeleri otomatik

### Yeni Akış

```
Kullanıcı Resmi
    ↓
FastAPI Backend (/chat-with-image)
    ↓
Kaggle API → Kaggle Notebook
    ↓
PlantCLEF Dataset (Kaggle'da)
    ↓
CLIP Encoding + Similarity Search
    ↓
Top-5 Predictions
    ↓
FastAPI Backend → Frontend
```

---

## 🔧 Yeni Bileşenler

### 1. Kaggle Notebook
**Dosya**: `notebooks/kaggle_plant_recognition.ipynb`

**Görevler**:
- ✅ CLIP model yükleme
- ✅ User image encoding
- ⏳ PlantCLEF dataset'ten similarity search
- ⏳ Top-5 predictions döndürme

**Nasıl Çalışır**:
1. Notebook Kaggle'a yüklenir
2. PlantCLEF 2025 dataset'i notebook'a eklenir
3. FastAPI backend Kaggle API ile notebook'u çağırır
4. Sonuçlar JSON olarak döner

### 2. Kaggle Notebook Service
**Dosya**: `backend/app/services/kaggle_notebook_service.py`

**Görev**: FastAPI'den Kaggle'a istek gönderme

```python
# Kullanım
result = await kaggle_notebook_service.submit_image_for_inference(
    image_bytes=user_image,
    image_name="user_plant.jpg"
)
# Returns: {"predictions": [...], "confidence": 0.95}
```

### 3. Weaviate Yeni Rol
**Eski**: Tüm PlantCLEF görselleri  
**Yeni**: Sadece user uploaded görseller

**Amaç**:
- User history (kullanıcının önceki sorguları)
- Favorites (favorilere eklenen bitkiler)
- Personalization (kişiselleştirilmiş öneriler)

---

## 📋 Güncellenen Roadmap

### ✅ Tamamlandı
1. Backend API (FastAPI)
2. Güvenlik katmanları
3. PostgreSQL database
4. API keys (Weaviate, OpenRouter, PlantNet, Kaggle)
5. Kaggle notebook template

### 🔨 Devam Ediyor
6. **Kaggle Notebook - Öncelik 1** 🔥
   - [ ] Notebook'u Kaggle'a yükle
   - [ ] PlantCLEF 2025 dataset ekle
   - [ ] Pre-compute embeddings (one-time)
   - [ ] Similarity search implement et
   - [ ] Test et

7. **Kaggle API Entegrasyonu - Öncelik 2** 🔥
   - [ ] `kaggle_notebook_service.py` tamamla
   - [ ] FastAPI'den Kaggle'a istek gönder
   - [ ] Response parsing
   - [ ] Error handling

8. **Frontend - Öncelik 3** 🔥
   - [ ] npm install
   - [ ] Backend'e bağlan
   - [ ] Image upload test et
   - [ ] Results görüntüle

9. **Weaviate - Öncelik 4** 🟠
   - [ ] User history için schema
   - [ ] Favorites için schema
   - [ ] Integration test

### ❌ İptal Edildi
- ~~Lokal dataset indirme~~
- ~~IDrive2 storage~~
- ~~Tüm görselleri Weaviate'e yükleme~~

---

## 🎯 Öncelikli Sonraki Adımlar

### Adım 1: Kaggle Notebook Tamamla (2-3 saat)
```bash
# 1. Notebook'u Kaggle'a yükle
# notebooks/kaggle_plant_recognition.ipynb

# 2. Kaggle'da aç ve dataset ekle
# "Add data" → "PlantCLEF 2025"

# 3. Pre-compute embeddings (tek sefer)
# Tüm PlantCLEF görsellerini encode et
# Embeddings'leri pickle olarak kaydet (~2GB)

# 4. Similarity search function
# Cosine similarity ile k-NN
```

### Adım 2: Kaggle API Entegrasyonu (1-2 saat)
```python
# backend/app/services/kaggle_notebook_service.py
async def submit_image_for_inference(image_bytes, image_name):
    # 1. Upload image to Kaggle
    # 2. Trigger notebook execution
    # 3. Poll for results (or webhook)
    # 4. Parse and return predictions
```

### Adım 3: End-to-End Test (30 dk)
```bash
# 1. Frontend'den resim yükle
# 2. Backend → Kaggle
# 3. Kaggle → PlantCLEF search
# 4. Results → Frontend
```

---

## 💡 Teknik Detaylar

### Kaggle API Kullanımı

**Notebook Çalıştırma**:
```python
from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()

# Push notebook
api.kernels_push("notebook-metadata.json")

# Get results
api.kernels_output("username/notebook-name", path="./output")
```

**Alternatif: Kaggle Kernel API**:
- Notebook'u public yap
- REST API endpoint oluştur
- FastAPI'den HTTP request gönder

### Pre-computed Embeddings

**Neden Gerekli**:
- PlantCLEF'de ~1M görsel var
- Her seferinde encode etmek çok yavaş (1M × 2s = 2M saniye = 23 gün!)
- Tek sefer encode → disk'e kaydet → hızlı search

**Dosya Boyutu**:
```
1M images × 512 dimensions × 4 bytes (float32) = 2GB
Compressed: ~500MB
```

**Search Hızı**:
- Pre-computed: ~50ms (sadece similarity hesabı)
- On-the-fly: ~2s (encode + similarity)

---

## 📊 Karşılaştırma

| Özellik | Eski Yaklaşım | Yeni Yaklaşım |
|---------|---------------|---------------|
| Dataset Storage | 1TB lokal | 0 (Kaggle'da) |
| IDrive2 | Gerekli | Gereksiz |
| GPU | Lokal gerekli | Kaggle ücretsiz |
| Setup Time | 1 gün (indirme) | 2 saat (notebook) |
| Monthly Cost | ~$20 | $0 |
| Maintenance | Yüksek | Düşük |
| Güncellemeler | Manuel | Otomatik |

---

## 🚀 Deployment Stratejisi

### Development (Şimdi)
- Kaggle notebook manuel çalıştır
- Test için yeterli

### Production (Sonra)
**Option 1: Kaggle Kernels API**
- Pro: Kolay setup
- Con: Rate limit var

**Option 2: Kaggle Dataset Snapshot**
- Pre-computed embeddings'i Kaggle'da dataset olarak yayınla
- Backend'de direkt oku (HTTP)
- Pro: Hızlı, rate limit yok
- Con: Embedding update için yeni snapshot

**Option 3: Hybrid**
- PlantNet API (hızlı, basit bitkiler)
- Kaggle (kompleks, nadir bitkiler)
- Weaviate (user history, favorites)

---

## ✅ Checklist

### Notebook Hazırlığı
- [x] Notebook template oluştur
- [ ] Kaggle'a yükle
- [ ] PlantCLEF 2025 dataset ekle
- [ ] GPU enable et
- [ ] Pre-compute embeddings
- [ ] Test et

### Backend Entegrasyonu
- [x] `kaggle_notebook_service.py` oluştur
- [ ] Kaggle API implement et
- [ ] Error handling
- [ ] Rate limiting
- [ ] Caching (Redis)

### Frontend
- [ ] npm install
- [ ] Test image upload
- [ ] Display Kaggle results
- [ ] Loading states

---

**Sonuç**: Çok daha basit, ucuz ve maintainable bir yaklaşım! 🎉

**Sonraki Adım**: Kaggle notebook'unu Kaggle'a yükle ve test et!
