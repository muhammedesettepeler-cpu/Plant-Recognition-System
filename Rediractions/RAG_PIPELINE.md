# 🌿 RAG Pipeline Architecture - Hybrid Plant Recognition

## Overview

This document describes the **Hybrid RAG (Retrieval-Augmented Generation)** pipeline used for intelligent plant identification. The system combines multiple data sources (Kaggle PlantCLEF, PlantNet, USDA) with LLM-powered Turkish language generation.

---

## 🔄 Complete Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                            │
│  User uploads image + question via FormData (binary, not base64)   │
│  Components: ImageUpload, PlantChatSection, usePlantChat hook      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                              │
│                   POST /api/v1/chat-with-image                      │
│                                                                     │
│  Security Pipeline:                                                 │
│  1. API Key Auth (optional)  4. MIME Verification                  │
│  2. Rate Limiting (10/min)   5. Magic Bytes Check                  │
│  3. Size Check (≤10MB)       6. PIL Sanitization                   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│              STEP 1: PARALLEL IMAGE RECOGNITION                     │
│                                                                     │
│  ┌─────────────────────────┐  ┌─────────────────────────┐          │
│  │   KAGGLE PLANTCLEF      │  │      PLANTNET API       │          │
│  │                         │  │                         │          │
│  │  • Gradio Remote API    │  │  • POST with image      │          │
│  │  • 1.5TB dataset        │  │  • Returns species      │          │
│  │  • ResNet model         │  │  • Common names         │          │
│  │  • Top-5 predictions    │  │  • Family info          │          │
│  │  • High accuracy        │  │  • GBIF ID              │          │
│  └───────────┬─────────────┘  └───────────┬─────────────┘          │
│              │                            │                         │
│              └────────────┬───────────────┘                         │
│                           ▼                                         │
│                   Merge & Prioritize                                │
│           (Kaggle primary, PlantNet enrichment)                     │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│              STEP 2: USDA VALIDATION & ENRICHMENT                   │
│                                                                     │
│  For each identified plant:                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  usda_service.find_by_scientific_name("Rosa damascena")     │   │
│  │                                                              │   │
│  │  Weaviate Query (93,158 plants):                            │   │
│  │  • Text search on scientificName                            │   │
│  │  • Returns: symbol, commonName, family                      │   │
│  │  • Mark as usda_verified: true if found                     │   │
│  │  • Fill missing fields (family, common name)                │   │
│  └─────────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│              STEP 3: CONTEXT BUILDING                               │
│                                                                     │
│  Build Turkish prompt for LLM:                                      │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  BULUNAN BİTKİLER:                                          │   │
│  │                                                              │   │
│  │  - Rosa damascena (Damascus Rose)                           │   │
│  │    Aile: Rosaceae                                           │   │
│  │    Güven: 95.0%                                             │   │
│  │    Kaynak: kaggle-plantclef, ✓ USDA Doğrulandı             │   │
│  │                                                              │   │
│  │  - Rosa gallica (French Rose)                               │   │
│  │    Aile: Rosaceae                                           │   │
│  │    Güven: 87.0%                                             │   │
│  │    Kaynak: plantnet, ✓ USDA Doğrulandı                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│              STEP 4: LLM RESPONSE GENERATION                        │
│                                                                     │
│  Priority Order:                                                    │
│  1. Google Gemini 2.0 Flash (GOOGLE_AI_STUDIO_API_KEY)             │
│  2. OpenRouter Nemotron (OPENROUTER_API_KEY)                       │
│  3. Template-based fallback (no API needed)                        │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  System: Sen bir botanik uzmanısın. Türkçe yanıt ver.       │   │
│  │                                                              │   │
│  │  Context: [TOP 3 PLANTS WITH DETAILS]                       │   │
│  │                                                              │   │
│  │  User Query: [SANITIZED USER MESSAGE]                       │   │
│  │                                                              │   │
│  │  → Generate contextual Turkish response                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│              STEP 5: RESPONSE FORMATTING                            │
│                                                                     │
│  {                                                                  │
│    "session_id": "abc-123-def",                                    │
│    "response": "🌿 **Görsel Analizi Tamamlandı!**\n...",           │
│    "identified_plants": [                                          │
│      {                                                              │
│        "id": 1,                                                    │
│        "scientificName": "Rosa damascena",                         │
│        "commonName": "Damascus Rose",                              │
│        "family": "Rosaceae",                                       │
│        "confidence": 0.95,                                         │
│        "source": "kaggle-plantclef",                               │
│        "usda_verified": true                                       │
│      }                                                              │
│    ],                                                               │
│    "total_matches": 3,                                             │
│    "highest_confidence": 0.95,                                     │
│    "sources": {                                                    │
│      "kaggle": 2,                                                  │
│      "plantnet": 1,                                                │
│      "usda_verified": 2                                            │
│    },                                                               │
│    "image_hash": "a1b2c3d4...",                                    │
│    "timestamp": "2026-01-06T17:00:00Z"                             │
│  }                                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Key Components

### 1. **CLIP Service** (`clip_service.py`)

```python
# Advanced preprocessing pipeline
def _advanced_preprocessing(image):
    1. RGB conversion
    2. fastNlMeansDenoisingColored (OpenCV)
    3. Sharpness enhancement (factor 1.3)
    4. Auto contrast (factor 1.2)
    5. Color enhancement (factor 1.15)
    return processed_image

# Test-Time Augmentation
def _multi_crop_augmentation(image):
    crops = [
        center_crop,
        top_left_corner,
        top_right_corner,
        bottom_left_corner,
        bottom_right_corner
    ]
    return crops  # 5 variants

# Final embedding
embedding = average(encode_image(crop) for crop in crops)
embedding = L2_normalize(embedding)  # 512-dim vector
```

### 2. **Kaggle Notebook Service** (`kaggle_notebook_service.py`)

```python
# Gradio API integration
async def identify_plant(image_bytes, top_k=5):
    # 1. Convert to base64
    image_base64 = base64.b64encode(buffer.getvalue())
    
    # 2. POST to Gradio API
    response = await client.post(
        f"{notebook_url}/gradio_api/call/predict",
        json={"data": [{"url": f"data:image/jpeg;base64,{image_base64}"}]}
    )
    
    # 3. Get event_id and fetch result
    event_id = response.json()["event_id"]
    result = await client.get(f".../predict/{event_id}")
    
    # 4. Parse SSE response
    return format_predictions(result)
```

### 3. **USDA Service** (`usda_service.py`)

```python
# Weaviate text search
def find_by_scientific_name(scientific_name):
    result = client.query.get("USDAPlant", [
        "symbol", "scientificName", "commonName", "family"
    ]).with_bm25(
        query=scientific_name,
        properties=["scientificName"]
    ).with_limit(1).do()
    
    return result["data"]["Get"]["USDAPlant"][0]
```

### 4. **LLM Service** (`grok_service.py`)

```python
# Template-based fallback (no external API needed)
def _generate_plant_response(prompt, context):
    response_parts = ["🌿 **Görsel Analizi Tamamlandı!**\n"]
    response_parts.append("**Bulunan Bitkiler:**")
    response_parts.append(context)
    
    # Add contextual tips based on query
    if "bakım" in query_lower:
        response_parts.append("**💡 Bakım Önerileri:**")
        ...
    
    return "\n".join(response_parts)
```

---

## 🎯 Advantages of This Architecture

### ✅ Hybrid Recognition
| Source | Strength | Data Size |
|--------|----------|-----------|
| Kaggle PlantCLEF | High accuracy, specialized model | 1.5TB |
| PlantNet | Common names, GBIF IDs | API |
| USDA | Validation, US plant coverage | 93K plants |

### ✅ Multi-LLM Support
```
1. Google Gemini → Preferred (fast, accurate)
2. OpenRouter → Fallback (free tier)
3. Templates → Offline (no API needed)
```

### ✅ USDA Verification
- Validates scientific names against authoritative database
- Adds `usda_verified: true` flag for trusted results
- Enriches missing family/common name data

### ✅ Turkish Language
- All prompts and responses in Turkish
- Context-aware answers based on query type
- Care tips, toxicity warnings, etc.

---

## 📊 Performance Metrics

| Component | Latency | Notes |
|-----------|---------|-------|
| Image upload | ~50ms | FormData binary |
| Security checks | ~20ms | 6-layer validation |
| Kaggle API | ~3-5s | Remote Gradio inference |
| PlantNet API | ~1-2s | External API |
| USDA search | ~20ms | Weaviate Cloud BM25 |
| LLM generation | ~1-3s | Depends on provider |
| **Total** | **~5-10s** | End-to-end |

---

## 🔧 Configuration

### Environment Variables

```bash
# Kaggle Notebook (PlantCLEF inference)
KAGGLE_NOTEBOOK_URL=https://xxxx.gradio.live

# PlantNet (plant identification)
PLANTNET_API_KEY=your_key

# LLM (response generation)
GOOGLE_AI_STUDIO_API_KEY=your_key  # Primary
OPENROUTER_API_KEY=your_key        # Fallback

# USDA in Weaviate (validation)
WEAVIATE_URL=https://xxx.weaviate.cloud
WEAVIATE_API_KEY=your_key
```

---

## 🛠️ Usage Example

### Frontend (React)
```javascript
const handleSend = async () => {
  const formData = new FormData();
  formData.append('file', selectedImage);
  formData.append('message', 'Bu bitki nedir?');
  formData.append('session_id', sessionId);

  const response = await chatAPI.sendImageMessage(formData);
  
  console.log(response.data.response);
  console.log(response.data.identified_plants);
  console.log(response.data.sources.usda_verified);
};
```

### cURL
```bash
curl -X POST http://localhost:8000/api/v1/chat-with-image \
  -F "file=@rose.jpg" \
  -F "message=Bu çiçeğin bakımı nasıl yapılır?"
```

---

## 🚀 Future Improvements

- [ ] CLIP fine-tuning on PlantCLEF dataset
- [ ] Streaming LLM responses
- [ ] Redis caching for repeat queries
- [ ] Batch image processing
- [ ] Multi-language support
- [ ] Confidence thresholding

---

## 📚 References

- **CLIP Paper**: [Learning Transferable Visual Models](https://arxiv.org/abs/2103.00020)
- **Weaviate Docs**: [BM25 Search](https://weaviate.io/developers/weaviate/search/bm25)
- **RAG Pattern**: [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401)
- **PlantCLEF**: [LifeCLEF Plant Identification](https://www.imageclef.org/node/311)

---

**Last Updated**: January 2026
