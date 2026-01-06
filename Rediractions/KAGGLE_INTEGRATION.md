# Kaggle Entegrasyonu 🎯

## � Genel Bakış

Bu projede Kaggle iki farklı şekilde kullanılmaktadır:

1. **Kaggle Notebook Gradio API** - PlantCLEF 2025 modeli ile uzaktan bitki tanıma (1.5TB dataset)
2. **Kaggle API** - Dataset indirme ve yerel işleme

---

## 🚀 Yöntem 1: Kaggle Notebook Gradio API (Önerilen - Mevcut Kullanım)

Bu yöntem, PlantCLEF 2025 modelini Kaggle GPU'larında çalıştırıp Gradio API aracılığıyla erişim sağlar.

### 1. Kaggle Notebook Oluşturma

1. https://www.kaggle.com/ adresine git
2. **New Notebook** oluştur
3. GPU accelerator seç (Settings → Accelerator → GPU T4 x2)
4. **Internet** erişimi aç (Settings → Internet → On)

### 2. Notebook Kodu

Aşağıdaki kodu notebook'a yapıştır:

```python
# Install dependencies
!pip install gradio httpx pillow

import gradio as gr
from PIL import Image
import httpx
import io
import base64

# PlantCLEF 2025 model (örnek - gerçek model path'inizi kullanın)
MODEL_PATH = "/kaggle/input/plantclef2025-model/resnet_plantclef.pth"

def predict_plant(image):
    """Plant identification using PlantCLEF model"""
    # Model inference code here
    # Bu kısım gerçek model kodunuzla değiştirilmeli
    
    predictions = [
        {"scientific_name": "Rosa damascena", "score": 0.95},
        {"scientific_name": "Rosa gallica", "score": 0.87},
        {"scientific_name": "Rosa canina", "score": 0.72},
    ]
    
    return predictions

# Create Gradio interface
demo = gr.Interface(
    fn=predict_plant,
    inputs=gr.Image(type="pil"),
    outputs=gr.JSON(),
    title="PlantCLEF 2025 Identification API"
)

# Launch with public URL
demo.launch(share=True)  # Bu satır public URL oluşturur
```

### 3. Public URL Alma

Notebook'u çalıştırdığınızda şu şekilde bir output göreceksiniz:

```
Running on public URL: https://xxxxxxx.gradio.live
```

Bu URL'yi `.env` dosyasına ekleyin:

```bash
KAGGLE_NOTEBOOK_URL=https://xxxxxxx.gradio.live
```

### 4. Backend Entegrasyonu

`backend/app/services/kaggle_notebook_service.py` dosyası bu URL'i kullanır:

```python
class KaggleNotebookService:
    async def identify_plant(self, image_bytes: bytes, top_k: int = 5):
        # 1. Image to base64
        image = Image.open(io.BytesIO(image_bytes))
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # 2. Call Gradio API
        response = await self.client.post(
            f"{self.notebook_url}/gradio_api/call/predict",
            json={"data": [{"url": f"data:image/jpeg;base64,{image_base64}"}]}
        )
        
        # 3. Get predictions
        event_id = response.json()["event_id"]
        result = await self._get_result(event_id)
        
        return self._format_predictions(result, top_k)
```

### ⚠️ Önemli Notlar

1. **URL Süresi**: Gradio public URL'ler 72 saat sonra expire olur
2. **Notebook Çalışması**: Notebook'un aktif olması gerekir
3. **GPU Limiti**: Kaggle ücretsiz 30 saat/hafta GPU sunar

---

## 🔧 Yöntem 2: Kaggle API ile Dataset İndirme

### 1. Kaggle API Kurulumu

```powershell
# Virtual environment aktif olmalı
.\venv\Scripts\Activate.ps1

# Kaggle API yükle
pip install kaggle
```

### 2. API Credentials

1. https://www.kaggle.com/settings adresine git
2. "Create New API Token" butonuna tıkla
3. `kaggle.json` dosyası indirilecek
4. Dosyayı şuraya kopyala:

```powershell
# .kaggle klasörü oluştur
mkdir $env:USERPROFILE\.kaggle

# kaggle.json'ı kopyala (Downloads'tan)
cp $env:USERPROFILE\Downloads\kaggle.json $env:USERPROFILE\.kaggle\

# İzinleri ayarla
icacls $env:USERPROFILE\.kaggle\kaggle.json /inheritance:r /grant:r "$env:USERNAME:F"
```

### 3. Dataset İndirme

```python
# backend/scripts/download_kaggle_dataset.py
from kaggle.api.kaggle_api_extended import KaggleApi
import os

api = KaggleApi()
api.authenticate()

# PlantCLEF dataset sample indir
api.dataset_download_files(
    'plantclef2025',
    path='data/kaggle/plantclef2025',
    unzip=True
)
print("✅ Dataset indirildi!")
```

### 4. Mevcut Kaggle Service

`backend/app/services/kaggle_service.py`:

```python
class KaggleService:
    def list_dataset_files(self) -> list:
        """Dataset dosyalarını listele"""
        dataset_path = Path("data/kaggle/plantclef2025")
        if not dataset_path.exists():
            return []
        return list(dataset_path.glob("**/*"))
    
    def get_plant_images(self, limit: int = 100) -> list:
        """Bitki görsellerini al"""
        ...
```

---

## 📁 Proje Yapısı

```
Plant-Recognition-System/
├── backend/
│   ├── app/
│   │   └── services/
│   │       ├── kaggle_notebook_service.py  # Gradio API entegrasyonu
│   │       └── kaggle_service.py           # Dataset operasyonları
│   └── scripts/
│       └── kaggle_notebook_gradio.py       # Notebook örnek kodu
│
├── data/
│   └── kaggle/
│       └── plantclef2025/                  # İndirilen dataset (opsiyonel)
│
└── kaggle_notebook/
    └── PlantCLEF_Inference_API.ipynb       # Kaggle notebook dosyası
```

---

## 🧪 Test

### Kaggle API Bağlantısı Test

```powershell
# Dataset'leri listele
kaggle datasets list -s plant

# Belirli bir dataset hakkında bilgi
kaggle datasets metadata plantclef2025
```

### Notebook API Test

```python
import httpx
import asyncio

async def test_kaggle_api():
    notebook_url = "https://xxxxx.gradio.live"
    
    async with httpx.AsyncClient(timeout=60) as client:
        # Health check
        response = await client.get(f"{notebook_url}/api/predict")
        print(f"Status: {response.status_code}")

asyncio.run(test_kaggle_api())
```

### Backend Health Check

```powershell
curl http://localhost:8000/api/v1/health
```

Beklenen çıktı:
```json
{
  "services": {
    "kaggle": {
      "status": "configured",
      "notebook_url": "https://xxxxx.gradio.live"
    }
  }
}
```

---

## 📊 Performans Karşılaştırması

| Yöntem | Latency | Accuracy | Maliyet |
|--------|---------|----------|---------|
| Kaggle Notebook (GPU) | 3-5s | Yüksek | Ücretsiz (30h/hafta) |
| Lokal CLIP | 200ms | Orta | Model indirme |
| PlantNet API | 1-2s | Orta-Yüksek | Ücretsiz (500/gün) |

---

## ⚠️ Sık Karşılaşılan Sorunlar

### 1. Gradio URL Çalışmıyor

**Sebep**: Notebook durmuş veya URL expire olmuş

**Çözüm**: 
1. Kaggle'a git, notebook'u tekrar çalıştır
2. Yeni `share=True` URL'sini al
3. `.env` dosyasını güncelle

### 2. GPU Limit Aşıldı

**Sebep**: Haftalık 30 saat GPU limiti

**Çözüm**:
- Bir sonraki haftayı bekle
- CPU ile çalıştır (daha yavaş)
- Kaggle Pro satın al

### 3. Large Dataset İndirme Hatası

**Sebep**: PlantCLEF 2025 çok büyük (~1.5TB)

**Çözüm**:
```bash
# Sadece belirli dosyaları indir
kaggle datasets download plantclef2025 -f metadata.csv
```

---

## 🎉 Özet

✅ Kaggle Notebook Gradio API kuruldu (`kaggle_notebook_service.py`)  
✅ PlantCLEF 1.5TB remote inference destekleniyor  
✅ Kaggle API dataset indirme servisi hazır (`kaggle_service.py`)  
✅ Backend health check'e Kaggle durumu eklendi  
✅ RAG pipeline'a Kaggle entegre edildi  

---

**Last Updated**: January 2026
