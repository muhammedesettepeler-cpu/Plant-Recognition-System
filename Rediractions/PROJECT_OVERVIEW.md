# 🌱 Plant Recognition System - Project Overview

## Proje Hakkında / About the Project

Bu proje, **LLM Destekli Akıllı Bitki Tanıma ve Bilgilendirme Sistemi** olarak tasarlanmış kapsamlı bir yapay zeka uygulamasıdır. Kullanıcılar bitki fotoğrafları yükleyerek bitki türlerini tanımlayabilir ve doğal dil ile sohbet ederek bitkiler hakkında bilgi alabilir.

This is a comprehensive **LLM-Supported Intelligent Plant Recognition and Information System**. Users can upload plant photos to identify species and chat naturally to learn about plants.

## 🎯 Ana Özellikler / Key Features

### 1. Görüntü Tanıma / Image Recognition
- **PlantNet API** entegrasyonu ile güçlü bitki tanıma
- **CLIP Model** ile görsel embedding ve benzerlik araması
- **OpenCV** ile görüntü ön işleme ve iyileştirme
- Yüklenen görüntülerden otomatik bitki bölgesi çıkarma

### 2. Vektör Tabanlı Arama / Vector Search
- **Weaviate** vektör veritabanı ile similarity search
- CLIP embeddings ile görsel benzerlik eşleştirme
- Hızlı ve doğru sonuçlar için optimize edilmiş

### 3. LLM Entegrasyonu / LLM Integration
- **Grok API** ile doğal dil yanıtları
- **RAG (Retrieval-Augmented Generation)** yaklaşımı
- Bağlama duyarlı, bilgilendirici açıklamalar

### 4. Chatbot Arayüzü / Chatbot Interface
- Doğal dilde soru-cevap
- Görüntü ile sohbet özelliği
- Konuşma geçmişi takibi
- Session yönetimi

### 5. Kapsamlı Veritabanı / Comprehensive Database
- **PostgreSQL**: Bitki metadata'sı
- **Weaviate**: Vektör embeddings
- **SQLAlchemy**: ORM yapısı
- Ölçeklenebilir veri modeli

## 📊 Teknik Mimari / Technical Architecture

### Backend Stack
```
FastAPI Application
├── API Endpoints
│   ├── /api/v1/recognize      # Bitki tanıma
│   ├── /api/v1/chat           # Metin sohbet
│   └── /api/v1/chat-with-image # Görüntülü sohbet
│
├── Services
│   ├── CLIP Service           # Görüntü embeddings
│   ├── Weaviate Service       # Vektör arama
│   ├── Grok Service           # LLM yanıtları
│   ├── PlantNet Service       # Bitki tanıma
│   ├── USDA Service           # Bitki bilgileri
│   └── IDrive Service         # Cloud storage
│
└── Database
    ├── PostgreSQL (Metadata)
    └── Weaviate (Vectors)
```

### Frontend Stack
```
React Application
├── Pages
│   ├── HomePage              # Ana sayfa
│   ├── RecognitionPage       # Görüntü tanıma
│   └── ChatbotPage          # Sohbet arayüzü
│
├── Components
│   └── Navigation           # Navigasyon menüsü
│
└── Material-UI Theme
    └── Green & Orange Palette
```

## 🔧 Kullanılan Teknolojiler / Technologies Used

### Yapay Zeka / AI & ML
- **CLIP**: `openai/clip-vit-base-patch32`
- **Transformers**: HuggingFace library
- **TensorFlow**: Görüntü işleme
- **OpenCV**: Bilgisayarlı görü
- **Grok**: Large Language Model

### API'ler / APIs
- **PlantNet API**: Bitki tanıma
- **Grok API**: LLM yanıtları
- **USDA Plants Database**: Bitki bilgileri
- **Trefle.io**: Bitki türleri

### Veritabanları / Databases
- **PostgreSQL 15**: İlişkisel veritabanı
- **Weaviate**: Vektör veritabanı
- **SQLAlchemy**: Python ORM

### Backend Framework
- **FastAPI**: Modern, hızlı web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Veri validasyonu
- **httpx**: Async HTTP client

### Frontend Framework
- **React 18**: UI library
- **Material-UI**: Komponent kütüphanesi
- **React Router**: Sayfa yönlendirme
- **Axios**: HTTP istekleri
- **react-dropzone**: Dosya yükleme

### DevOps & Infrastructure
- **Docker**: Konteynerizasyon
- **Docker Compose**: Multi-container orchestration
- **Grafana**: Monitoring
- **IDrive e2**: Cloud storage

## 📁 Proje Yapısı / Project Structure

```
Plant-Recognition-System/
├── backend/                   # FastAPI Backend
│   ├── app/
│   │   ├── api/              # REST API endpoints
│   │   ├── core/             # Konfigürasyon
│   │   ├── db/               # Veritabanı
│   │   ├── models/           # SQLAlchemy modelleri
│   │   ├── services/         # İş mantığı servisleri
│   │   ├── utils/            # Yardımcı fonksiyonlar
│   │   └── main.py           # Ana uygulama
│   ├── requirements.txt      # Python bağımlılıkları
│   ├── Dockerfile           
│   ├── .env.example
│   └── init_db.py           # Veritabanı başlatma
│
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── components/       # React komponentleri
│   │   ├── pages/            # Sayfalar
│   │   ├── App.js
│   │   └── index.js
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
├── notebooks/                 # Jupyter notebooks
│   └── dataset_processing.py
│
├── data/                      # Veri dosyaları
│   ├── raw/                  # Ham veri
│   └── processed/            # İşlenmiş veri
│
├── docker-compose.yml        # Docker servisleri
├── .gitignore
├── README.md                 # Ana dokümantasyon
├── DEVELOPMENT.md            # Geliştirme kılavuzu
└── setup.ps1                 # Kurulum scripti
```

## 🚀 Hızlı Başlangıç / Quick Start

### Ön Gereksinimler / Prerequisites
```
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git
```

### 1. Projeyi Klonlayın
```bash
git clone https://github.com/muhammedesettepeler-cpu/Plant-Recognition-System.git
cd Plant-Recognition-System
```

### 2. Otomatik Kurulum (PowerShell)
```powershell
.\setup.ps1
```

### 3. Docker ile Çalıştırma
```bash
docker-compose up -d
```

### 4. Manuel Kurulum

**Backend:**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# .env dosyasını düzenleyin
python init_db.py
uvicorn app.main:app --reload
```

**Frontend:**
```powershell
cd frontend
npm install
npm start
```

## 🔑 API Anahtarları / API Keys Required

1. **Grok API**: https://x.ai/
2. **PlantNet API**: https://my.plantnet.org/
3. **IDrive e2** (opsiyonel): https://www.idrive.com/e2/

## 📖 Kullanım / Usage

### Web Arayüzü
1. Ana sayfa: `http://localhost:3000`
2. Bitki tanıma: Upload fotoğraf → Tanımla
3. Chatbot: Soru yazın veya görüntü ekleyin

### API Kullanımı
API Dokümantasyonu: `http://localhost:8000/docs`

**Bitki Tanıma:**
```bash
curl -X POST http://localhost:8000/api/v1/recognize \
  -F "file=@plant.jpg"
```

**Chatbot:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What plants need full sun?"}'
```

## 🎓 Proje Hedefleri / Project Goals

1. ✅ Modern AI teknolojilerini entegre etmek
2. ✅ Kullanıcı dostu bir arayüz sunmak
3. ✅ Ölçeklenebilir mimari tasarlamak
4. ✅ RAG yaklaşımı ile doğru bilgi vermek
5. ✅ Botanik meraklılarına yardımcı olmak

## 🔮 Gelecek Geliştirmeler / Future Enhancements

- [ ] Mobil uygulama (React Native)
- [ ] Offline mod desteği
- [ ] Çoklu dil desteği
- [ ] Kullanıcı hesapları ve favoriler
- [ ] Bitki bakım takvimleri
- [ ] Topluluk özellikleri
- [ ] Augmented Reality (AR) entegrasyonu
- [ ] Daha fazla veri kaynağı entegrasyonu

## 📊 Performans / Performance

- **Tanıma Süresi**: ~2-5 saniye
- **Doğruluk**: %85-95 (PlantNet + CLIP)
- **Vektör Arama**: <100ms
- **LLM Yanıt**: 1-3 saniye

## 🤝 Katkıda Bulunma / Contributing

1. Fork yapın
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Branch'inizi push edin
5. Pull Request açın

## 📄 Lisans / License

MIT License - Detaylar için LICENSE dosyasına bakın

## 👨‍💻 Geliştirici / Developer

**Muhammed Esettepeler**
- GitHub: [@muhammedesettepeler-cpu](https://github.com/muhammedesettepeler-cpu)

## 🙏 Teşekkürler / Acknowledgments

- PlantNet ekibine
- OpenAI CLIP modeli için
- Weaviate topluluğuna
- React ve FastAPI geliştiricilerine

---

**Not**: Bu proje eğitim amaçlıdır ve modern AI teknolojilerinin botanik uygulamalarına entegrasyonunu göstermektedir.

**Note**: This is an educational project demonstrating the integration of modern AI technologies in botanical applications.
