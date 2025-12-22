# 🌱 Plant Recognition System
## LLM-Supported Intelligent Plant Recognition and Information System

An AI-powered web application that identifies plants from images and provides detailed botanical information through natural language interactions.

## 🎯 Proje Özeti / Project Summary

Bu projenin amacı, kullanıcıların yüklediği bitki görsellerini yapay zekâ desteğiyle tanıyarak ilgili bilgileri otomatik olarak sunan bir sistem geliştirmektir. Sistem, görsel veriyi analiz ederek benzer bitkileri veri tabanındaki kayıtlarla eşleştirir ve Large Language Model (LLM) desteğiyle kullanıcıya doğal dilde açıklamalar üretir. 

This system combines computer vision, vector databases, and large language models to create an intelligent botanical assistant. Users can upload plant images or chat with an AI assistant to learn about various plant species.

### Özellikler / Key Features

- **Görüntü Tanıma / Image Recognition**: PlantNet API ve CLIP embeddings ile anlık bitki tanıma
- **Benzerlik Arama / Similarity Search**: Weaviate vektör veritabanı ile görsel benzerlik arama
- **Chatbot Arayüzü / Chatbot Interface**: Nvidia LLM destekli doğal dil etkileşimi
- **RAG Mimarisi**: Retrieval-Augmented Generation ile hassas yanıtlar
- **Kapsamlı Veritabanı**: PostgreSQL (metadata) + Weaviate (vektörler)
- **Görüntü İşleme**: OpenCV ve TensorFlow ile gelişmiş ön işleme


##  Kullanılan Teknolojiler / Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL (metadata) + Weaviate Cloud (vectors)
- **ORM**: SQLAlchemy
- **AI/ML**:
  - CLIP (openai/clip-vit-base-patch32) for embeddings
  - PlantNet API for plant identification
  - Nvidia Free API for LLM responses
- **Görüntü İşleme**: OpenCV, TensorFlow Image, Pillow


### Frontend
- **Framework**: React.js
- **UI Library**: Material-UI (MUI)
- **File Upload**: react-dropzone
- **HTTP Client**: Axios

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Monitoring**: Grafana
- **Web Server**: Uvicorn

### Veri Kaynakları / Data Sources
- **Kaggle**: Dataset için
- **PlantNet API**: Görüntü tanıma
- **USDA Plants Database**: Bitki bilgileri
- **Trefle.io**: Bitki türleri verisi

##  Architecture

```
┌─────────────────┐
│   React Frontend│
│   Material UI   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Backend│
├─────────────────┤
│ - PlantNet API  │
│ - CLIP Model    │
│ - Nvidia LLM    │
│ - RAG Pipeline  │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌──────┐  ┌──────────┐
│ Post │  │ Weaviate │
│ greSQL│  │  Vector  │
└──────┘  └──────────┘
```

##  Project Structure

```
Plant-Recognition-System/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   │   ├── health.py
│   │   │   ├── plant_recognition.py
│   │   │   └── chatbot.py
│   │   ├── core/             # Configuration
│   │   │   └── config.py
│   │   ├── db/               # Database setup
│   │   │   └── base.py
│   │   ├── models/           # SQLAlchemy models
│   │   │   └── plant.py
│   │   ├── services/         # Business logic
│   │   │   ├── clip_service.py
│   │   │   ├── weaviate_service.py
│   │   │   ├── grok_service.py
│   │   │   └── plantnet_service.py
│   │   ├── utils/            # Utilities
│   │   │   └── image_utils.py
│   │   └── main.py           # FastAPI app
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Navigation.js
│   │   ├── pages/
│   │   │   ├── HomePage.js
│   │   │   ├── RecognitionPage.js
│   │   │   └── ChatbotPage.js
│   │   ├── App.js
│   │   └── index.js
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── notebooks/                # Jupyter notebooks for experiments
├── data/                     # Dataset storage
├── docker-compose.yml
└── README.md
```

##  Kurulum / Getting Started

### Gereksinimler / Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- API Keys:
  - Nvidia API key
  - PlantNet API key
  - Weaviate Cloud API key (optional)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/muhammedesettepeler-cpu/Plant-Recognition-System.git
cd Plant-Recognition-System
```

2. **Setup environment variables**
```bash
cd backend
cp .env.example .env
# .env dosyasını düzenleyin ve API anahtarlarınızı ekleyin
```

3. **Docker ile Başlatın / Start with Docker**
```bash
docker-compose up -d
```

Bu şunları başlatır:
- PostgreSQL: port 5432
- Weaviate: port 8080
- Backend API: port 8000
- Frontend: port 3000
- Grafana: port 3001

4. **Uygulamaya Erişim / Access**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Grafana: http://localhost:3001 (admin/admin)

### Manuel Kurulum / Manual Setup (Development)

#### Backend

```powershell
cd backend

# Sanal ortam oluştur
python -m venv venv
.\venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Sunucuyu başlat
uvicorn app.main:app --reload
```

#### Frontend

```powershell
cd frontend

# Bağımlılıkları yükle
npm install

# Development server başlat
npm start
```

## 📚 API Documentation

### Endpoints

#### Health Check
```
GET /api/v1/health
GET /api/v1/status
```

#### Plant Recognition
```
POST /api/v1/recognize
- Bitki görüntüsü yükle ve tanımla
- Returns: PlantNet sonuçları, benzerlik eşleşmeleri, LLM açıklaması

POST /api/v1/analyze-image
- Bitki görüntüsünü analiz et ve iyileştir
```

#### Chatbot
```
POST /api/v1/chat
- RAG ile metin tabanlı bitki sorguları

POST /api/v1/chat-with-image
- Görüntü eki ile sohbet

GET /api/v1/conversation-history/{session_id}
- Konuşma geçmişini getir
```

## 🔧 Configuration

Tüm yapılandırma seçenekleri için `backend/.env.example` dosyasına bakın.

Ana değişkenler:
- `GROK_API_KEY`: Grok API anahtarınız
- `PLANTNET_API_KEY`: PlantNet API anahtarı
- `POSTGRES_*`: Veritabanı yapılandırması
- `WEAVIATE_URL`: Vektör veritabanı URL'si
- `IDRIVE_*`: Bulut depolama kimlik bilgileri

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 👥 Yazar / Author

- Muhammed Esettepeler
- Ramazan Bugra Sahin
## 📝 License

This project is licensed under the FSMVU License.

---

**Not**: Bu, modern AI teknolojilerinin botanik uygulamalarına entegrasyonunu göstermek için geliştirilmiş eğitici bir projedir.
