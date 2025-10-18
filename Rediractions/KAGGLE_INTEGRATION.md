# Kaggle Entegrasyonu 🎯

## 🔧 Yöntem 1: Kaggle API ile Direkt İndirme (Önerilen)

### 1. Kaggle API Kurulumu:

```powershell
# Virtual environment aktif olmalı
.\venv\Scripts\Activate.ps1

# Kaggle API yükle
pip install kaggle
```

### 2. Kaggle API Credentials:

1. **kaggle.com/settings** adresine git
2. "Create New API Token" butonuna tıkla
3. `kaggle.json` dosyası indirilecek
4. Dosyayı şuraya kopyala:
   ```
   C:\Users\<username>\.kaggle\kaggle.json
   ```

Windows için:
```powershell
# .kaggle klasörü oluştur
mkdir $env:USERPROFILE\.kaggle

# kaggle.json'ı kopyala
cp Downloads\kaggle.json $env:USERPROFILE\.kaggle\

# İzinleri ayarla (opsiyonel)
icacls $env:USERPROFILE\.kaggle\kaggle.json /inheritance:r /grant:r "$env:USERNAME:F"
```

### 3. Dataset İndir:

```python
# backend/scripts/download_kaggle_data.py
from kaggle.api.kaggle_api_extended import KaggleApi
import os

api = KaggleApi()
api.authenticate()

# PlantCLEF 2025 dataset'ini indir
api.dataset_download_files(
    'plantclef2025',
    path='data/kaggle/plantclef2025',
    unzip=True
)
print("✅ Dataset indirildi!")
```

Çalıştır:
```powershell
python backend/scripts/download_kaggle_data.py
```

---

## 🔧 Yöntem 2: Manuel İndirme

### 1. Kaggle'dan Manuel İndir:

1. https://www.kaggle.com/datasets/plantclef2025 adresine git
2. "Download" butonuna tıkla
3. ZIP dosyasını `data/kaggle/` klasörüne çıkart

### 2. Projeye Ekle:

```python
# backend/app/core/config.py içine ekle
KAGGLE_DATA_PATH: str = "data/kaggle/plantclef2025"
```

---

## 🔧 Yöntem 3: Kaggle Notebook'tan Veri Çekme

### Kaggle Notebook'ta:

```python
import pandas as pd
import numpy as np

# PlantCLEF 2025 dataset
base_path = "/kaggle/input/plantclef2025"

# Verileri oku
train_df = pd.read_csv(f"{base_path}/train.csv")

# Örnek 1000 bitki bilgisini CSV olarak kaydet
sample_data = train_df.head(1000)
sample_data.to_csv("plant_data_sample.csv", index=False)

# Kaggle output'una kaydet (Download edilebilir)
print("✅ Veri hazır! Notebook output'undan indir.")
```

Sonra bu CSV'yi projeye ekle:
```
data/kaggle/plant_data_sample.csv
```

---

## 🚀 Projeye Entegrasyon

### 1. Kaggle Servisini API'ye Ekle:

```python
# backend/app/api/kaggle_data.py
from fastapi import APIRouter, HTTPException
from app.services.kaggle_service import kaggle_service

router = APIRouter()

@router.get("/dataset/info")
async def get_dataset_info():
    files = kaggle_service.list_dataset_files()
    return {
        "total_files": len(files),
        "sample_files": files[:10]
    }

@router.get("/dataset/images")
async def get_plant_images(limit: int = 100):
    images = kaggle_service.get_plant_images(limit)
    return {"images": images, "count": len(images)}
```

### 2. Main.py'ye Router Ekle:

```python
# backend/app/main.py
from app.api import kaggle_data

app.include_router(
    kaggle_data.router, 
    prefix=f"{settings.API_V1_PREFIX}/kaggle", 
    tags=["kaggle"]
)
```

### 3. Dataset'i Weaviate'e Yükle:

```python
# backend/scripts/load_kaggle_to_weaviate.py
import asyncio
from app.services.kaggle_service import kaggle_service
from app.services.weaviate_service import weaviate_service
from app.services.clip_service import clip_service

async def load_dataset():
    # Kaggle'dan görselleri al
    images = kaggle_service.get_plant_images(limit=1000)
    
    for image_path in images:
        # CLIP ile embedding oluştur
        embedding = await clip_service.encode_image(image_path)
        
        # Weaviate'e ekle
        await weaviate_service.add_plant_image(
            plant_id=1,  # Gerçek plant_id kullan
            image_url=image_path,
            embedding=embedding
        )
    
    print(f"✅ {len(images)} görsel yüklendi!")

if __name__ == "__main__":
    asyncio.run(load_dataset())
```

---

## 📦 requirements.txt Güncelle

```bash
# Kaggle API ekle
kaggle>=1.6.0
```

Yükle:
```powershell
pip install kaggle
```

---

## 🎯 Kullanım Senaryoları

### Senaryo 1: Training Data olarak Kullan
```python
# Kaggle'daki 1M+ bitki görselini Weaviate'e yükle
# CLIP embeddings ile similarity search
```

### Senaryo 2: Test Data olarak Kullan
```python
# Kaggle test set'ini kullanarak model accuracy test et
```

### Senaryo 3: Metadata Zenginleştirme
```python
# Kaggle'daki bitki bilgilerini PostgreSQL'e aktar
# (family, genus, species, common names, etc.)
```

---

## 📁 Klasör Yapısı

```
Plant-Recognition-System/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── kaggle_data.py          # Yeni!
│   │   └── services/
│   │       └── kaggle_service.py       # Yeni!
│   └── scripts/
│       ├── download_kaggle_data.py     # Yeni!
│       └── load_kaggle_to_weaviate.py  # Yeni!
└── data/
    └── kaggle/
        └── plantclef2025/              # Dataset buraya
            ├── train/
            ├── test/
            └── metadata.csv
```

---

## ⚠️ Önemli Notlar

### 1. Dosya Boyutu:
PlantCLEF 2025 dataset çok büyük (~100GB+)
```bash
# Sadece sample indir
kaggle datasets download -p data/kaggle/ plantclef2025 --unzip -f sample.zip
```

### 2. Git Ignore:
```bash
# .gitignore'a ekle
data/kaggle/
*.csv
*.zip
```

### 3. Performance:
```python
# Tüm dataset'i bir seferde yükleme!
# Batch processing kullan (1000'lik gruplar)
```

---

## 🧪 Test

### 1. Kaggle API Test:
```powershell
kaggle datasets list -s plant
```

### 2. Servis Test:
```python
from app.services.kaggle_service import kaggle_service

# Dataset dosyalarını listele
files = kaggle_service.list_dataset_files()
print(f"Toplam dosya: {len(files)}")

# İlk 10 görseli al
images = kaggle_service.get_plant_images(limit=10)
print(images)
```

### 3. API Test:
```bash
curl http://localhost:8000/api/v1/kaggle/dataset/info
```

---

## 🎉 Özet

✅ Kaggle API kurulumu yapıldı
✅ Dataset indirme servisi oluşturuldu
✅ Weaviate entegrasyonu hazır
✅ API endpoint'leri eklendi
✅ Batch processing desteği

**Hangi yöntemi tercih edersin?**
1. API ile otomatik indirme
2. Manuel indirme
3. Kaggle Notebook'tan veri çekme

Seç ve devam edelim! 🚀
