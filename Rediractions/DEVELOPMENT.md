# Development Quick Start Guide

## 🚀 First Time Setup

### 1. Backend Setup (PowerShell)

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env and add your API keys
notepad .env
```

### 2. Configure Environment Variables

Edit `backend/.env` with your API keys:

```bash
# Required APIs
PLANTNET_API_KEY=your_plantnet_key          # https://my.plantnet.org/
GOOGLE_AI_STUDIO_API_KEY=your_gemini_key    # https://aistudio.google.com/

# Weaviate Cloud (for USDA data)
WEAVIATE_URL=https://YOUR_CLUSTER.weaviate.cloud
WEAVIATE_API_KEY=your_weaviate_key
WEAVIATE_GRPC_HOST=grpc-YOUR_CLUSTER.weaviate.cloud

# Optional
KAGGLE_NOTEBOOK_URL=https://your-kaggle-gradio-url
OPENROUTER_API_KEY=your_openrouter_key      # Fallback LLM
REDIS_URL=redis://localhost:6379/0          # For rate limiting
```

### 3. Import USDA Data to Weaviate

```powershell
# Make sure virtual environment is active
.\venv\Scripts\activate

# Import 93K plants to Weaviate Cloud
python scripts/import_usda_to_weaviate.py

# Verify import
python scripts/test_weaviate.py
```

### 4. Run Backend Server

```powershell
# Start development server with hot reload
uvicorn app.main:app --reload
```

Backend will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

### 5. Frontend Setup (PowerShell)

```powershell
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will be available at: http://localhost:3000

---

## 🔑 Required API Keys

| API | Endpoint | Free Tier |
|-----|----------|-----------|
| **PlantNet** | https://my.plantnet.org/ | ✅ 500 req/day |
| **Google AI Studio** | https://aistudio.google.com/ | ✅ Free tier available |
| **Weaviate Cloud** | https://console.weaviate.cloud/ | ✅ Free sandbox |
| **OpenRouter** | https://openrouter.ai/ | ✅ Free models available |

---

## 🧪 Testing the System

### Test Health Endpoint
```powershell
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "usda_plants": { "status": "healthy", "plant_count": 93158 },
    "kaggle": { "status": "configured" },
    "plantnet": { "status": "configured" },
    "llm": { "status": "configured", "provider": "Google Gemini" },
    "redis": { "status": "not_connected" }
  }
}
```

### Test Plant Recognition with Image
```powershell
curl -X POST http://localhost:8000/api/v1/chat-with-image `
  -F "file=@path/to/your/plant/image.jpg" `
  -F "message=Bu bitki nedir?"
```

### Test Text Chat
```powershell
curl -X POST http://localhost:8000/api/v1/chat `
  -H "Content-Type: application/json" `
  -d '{"message": "Güller hakkında bilgi ver"}'
```

---

## 🐛 Common Issues & Solutions

### Port Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Weaviate Connection Error
1. Check `WEAVIATE_URL` and `WEAVIATE_API_KEY` in .env
2. Verify cluster is running at https://console.weaviate.cloud/
3. Check if USDA data is imported: `python scripts/test_weaviate.py`

### CLIP Model Loading Slow
First run downloads ~350MB model. Subsequent runs use cached model:
```
C:\Users\<username>\.cache\huggingface\
```

### Module Not Found
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Image Upload Error
- Check image size (max 10MB)
- Supported formats: JPEG, PNG, WebP, GIF
- Check if file is corrupted

---

## 🔄 Development Workflow

1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `npm start`
3. Make changes to code
4. Backend auto-reloads on Python file changes
5. Frontend hot-reloads on JS/CSS changes
6. Test via browser (http://localhost:3000) or API docs

---

## 📦 Useful Commands

### Backend
```powershell
# Run tests
pytest

# Run specific test
pytest tests/test_health.py -v

# Format code
black app/

# Check types
mypy app/

# Run with specific port
uvicorn app.main:app --reload --port 8001
```

### Frontend
```powershell
# Run tests
npm test

# Build for production
npm run build

# Lint
npm run lint

# Check bundle size
npm run analyze
```

---

## 🐳 Docker Quick Start (Alternative)

```powershell
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Run only databases
docker-compose up -d postgres weaviate redis
```

Services:
- PostgreSQL: localhost:5432
- Weaviate: localhost:8080
- Backend: localhost:8000
- Frontend: localhost:3000
- Grafana: localhost:3001 (admin/admin)

---

## 📁 Project File Overview

### Backend Key Files
| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app, lifespan, routers |
| `app/api/chatbot.py` | Main RAG pipeline |
| `app/services/clip_service.py` | CLIP embeddings |
| `app/services/usda_service.py` | USDA Weaviate queries |
| `app/core/config.py` | Pydantic settings |
| `app/core/security.py` | Image validation |

### Frontend Key Files
| File | Purpose |
|------|---------|
| `src/App.js` | Main app, routing |
| `src/pages/InteractivePlantPage.js` | Main assistant UI |
| `src/hooks/usePlantChat.js` | Chat state logic |
| `src/services/api.js` | Axios API client |

---

## 📚 Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **Material-UI**: https://mui.com/
- **Weaviate**: https://weaviate.io/developers/weaviate
- **CLIP**: https://github.com/openai/CLIP
- **PlantNet API**: https://my.plantnet.org/usage
- **Google AI Studio**: https://aistudio.google.com/

---

**Last Updated**: January 2026
