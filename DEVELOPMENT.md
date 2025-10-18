# Development Quick Start Guide

## First Time Setup

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

# Initialize database
python init_db.py

# Run development server
uvicorn app.main:app --reload
```

Backend will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

### 2. Frontend Setup (PowerShell)

```powershell
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will be available at: http://localhost:3000

### 3. Database Setup (Optional - using Docker)

```powershell
# Start PostgreSQL
docker run -d `
  --name plant_postgres `
  -e POSTGRES_USER=postgres `
  -e POSTGRES_PASSWORD=postgres `
  -e POSTGRES_DB=plant_recognition `
  -p 5432:5432 `
  postgres:15-alpine

# Start Weaviate
docker run -d `
  --name plant_weaviate `
  -p 8080:8080 `
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true `
  -e PERSISTENCE_DATA_PATH=/var/lib/weaviate `
  semitechnologies/weaviate:latest
```

## Required API Keys

1. **Grok API Key**: Get from https://x.ai/
2. **PlantNet API Key**: Get from https://my.plantnet.org/
3. **IDrive e2**: Get from https://www.idrive.com/e2/

## Testing the System

### Test Health Endpoint
```powershell
curl http://localhost:8000/api/v1/health
```

### Test Plant Recognition (with curl)
```powershell
curl -X POST http://localhost:8000/api/v1/recognize `
  -F "file=@path/to/your/plant/image.jpg"
```

### Test Chat Endpoint
```powershell
curl -X POST http://localhost:8000/api/v1/chat `
  -H "Content-Type: application/json" `
  -d '{\"message\": \"What is a rose?\"}'
```

## Common Issues

### Port Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Database Connection Error
- Check if PostgreSQL is running
- Verify credentials in .env file
- Ensure database 'plant_recognition' exists

### Module Not Found
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Development Workflow

1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `npm start`
3. Make changes to code
4. Backend auto-reloads
5. Frontend hot-reloads
6. Test via browser or API docs

## Useful Commands

### Backend
```powershell
# Run tests
pytest

# Format code
black app/

# Check types
mypy app/
```

### Frontend
```powershell
# Run tests
npm test

# Build for production
npm run build

# Lint
npm run lint
```

## Docker Quick Start (Alternative)

```powershell
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

## Next Steps

1. Add your PlantNet and Grok API keys to `.env`
2. Download a plant dataset from Kaggle
3. Process dataset using `notebooks/dataset_processing.py`
4. Test image recognition with sample images
5. Customize the UI in frontend/src

## Resources

- FastAPI Docs: https://fastapi.tiangolo.com/
- React Docs: https://react.dev/
- Material-UI: https://mui.com/
- Weaviate: https://weaviate.io/developers/weaviate
- CLIP: https://github.com/openai/CLIP
