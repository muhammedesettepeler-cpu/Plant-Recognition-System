# 📚 Kaggle PlantCLEF Integration - Quick Reference

## 🎯 Ne Yaptık?

✅ **Kaggle Notebook API** - PlantCLEF 2025 dataset için inference server
✅ **Backend Entegrasyonu** - Hybrid search (Weaviate + Kaggle)
✅ **Fallback Strategy** - Low confidence → Kaggle'a git
✅ **Health Check** - Kaggle durumu monitoring
✅ **Setup Guide** - KAGGLE_SETUP.md (detaylı)

---

## 🚀 Hızlı Başlangıç

### 1. Kaggle Notebook
- `kaggle_notebook/PlantCLEF_Inference_API.ipynb` → Kaggle'a yükle
- PlantCLEF 2025 dataset ekle
- Ngrok token ekle
- Run All

### 2. Backend .env
```bash
KAGGLE_NOTEBOOK_URL=https://your-ngrok-url.app
```

### 3. Test
```bash
curl http://localhost:8000/api/v1/health
# "kaggle_notebook": "available" görmeli
```

---

## 🔄 Pipeline

```
User uploads image
    ↓
CLIP encoding (backend)
    ↓
Weaviate search (14 plants, fast)
    ↓
If confidence < 70%
    ↓
Kaggle PlantCLEF (10k+ species, slower)
    ↓
Merge results
    ↓
LLM generates response
    ↓
Return to user
```

---

## 📁 Dosyalar

- `kaggle_notebook/PlantCLEF_Inference_API.ipynb` - Kaggle notebook
- `backend/app/services/kaggle_notebook_service.py` - Backend service
- `backend/app/api/chatbot.py` - Integration in RAG pipeline
- `KAGGLE_SETUP.md` - Detailed setup guide
- `README_KAGGLE.md` - This file

---

## 🎓 Detaylı Setup

Adım adım kurulum için: **[KAGGLE_SETUP.md](./KAGGLE_SETUP.md)**

---

## ✨ Benefits

- 📦 **No Download**: 1TB+ dataset indirmeye gerek yok
- 🚀 **Free GPU**: Kaggle'ın ücretsiz T4 GPU'su
- 🌍 **10k+ Species**: PlantCLEF 2025 tüm dataset
- ⚡ **Hybrid**: Local (fast) + Kaggle (comprehensive)
- 💰 **Free**: Tamamen ücretsiz!

---

**Status:** Ready to deploy! 🎉
