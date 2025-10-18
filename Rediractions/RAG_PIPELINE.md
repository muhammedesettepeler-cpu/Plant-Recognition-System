# 🌿 RAG Pipeline Architecture - Chatbot Image Recognition

## Overview
**Retrieval-Augmented Generation (RAG)** pipeline for intelligent plant identification using vision-language models and vector similarity search.

---

## 🔄 Complete Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                            │
│  User uploads image + question via FormData (binary, not base64)   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                              │
│                   POST /api/v1/chat-with-image                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ 1. Validation  │
                    │ - Size check   │
                    │ - Format check │
                    └────────┬───────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │ 2. Image Loading   │
                    │ - PIL Image.open   │
                    │ - RGB conversion   │
                    └────────┬───────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────┐
        │         3. CLIP Preprocessing              │
        │ - CLIPProcessor: resize, normalize         │
        │ - Convert to tensor (PyTorch)              │
        │ - Device placement (CPU/CUDA)              │
        └────────────────┬───────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────────┐
        │      4. CLIP Model Inference               │
        │ - CLIPModel.get_image_features()           │
        │ - Extract 512-dim embedding                │
        │ - L2 normalization (for cosine similarity) │
        │   embedding = features / ||features||      │
        └────────────────┬───────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────────┐
        │    5. Weaviate Vector Search               │
        │ - Query: normalized embedding (512-dim)    │
        │ - Method: cosine similarity                │
        │ - Returns: top-5 most similar plants       │
        │ - With certainty scores (0.0 - 1.0)        │
        └────────────────┬───────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────────┐
        │       6. RAG Context Building              │
        │ - Top-3 plants from vector DB              │
        │ - Format: scientific name + certainty      │
        │ - Example context:                         │
        │   "Similar plants:                         │
        │    - Rosa damascena (0.95 similarity)      │
        │    - Rosa gallica (0.89 similarity)"       │
        └────────────────┬───────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────────┐
        │    7. LLM Generation (OpenRouter)          │
        │ - Model: nvidia/nemotron-nano-9b-v2        │
        │ - Input: RAG context + user question       │
        │ - Output: Detailed, context-aware answer   │
        └────────────────┬───────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────────┐
        │         8. Response Return                 │
        │ {                                          │
        │   "session_id": "uuid",                    │
        │   "response": "LLM answer",                │
        │   "identified_plants": [...top 3],         │
        │   "confidence": 0.95,                      │
        │   "timestamp": "2025-10-18T..."            │
        │ }                                          │
        └────────────────────────────────────────────┘
```

---

## 📦 Key Components

### 1. **CLIP Service** (`clip_service.py`)
- **Model**: `openai/clip-vit-base-patch32`
- **Purpose**: Convert images/text to 512-dimensional embeddings
- **Key Features**:
  - Lazy loading (loads on first use)
  - RGB conversion
  - L2 normalization
  - GPU support (CUDA)

```python
# Embedding extraction
embedding = clip_service.encode_image(pil_image)
# Returns: [0.123, -0.456, ...] (512 floats, normalized)
```

### 2. **Weaviate Service** (`weaviate_service.py`)
- **Vector DB**: Weaviate Cloud
- **Similarity Metric**: Cosine distance
- **Purpose**: Find similar plants using vector embeddings

```python
# Similarity search
results = weaviate_service.similarity_search(embedding, limit=5)
# Returns: [
#   {"scientificName": "Rosa damascena", "_additional": {"certainty": 0.95}},
#   ...
# ]
```

### 3. **Grok Service** (`grok_service.py`)
- **LLM**: OpenRouter (nvidia/nemotron-nano-9b-v2:free)
- **Purpose**: Generate context-aware responses

```python
# RAG response
response = await grok_service.generate_rag_response(
    prompt="What is this flower?",
    context=similar_plants
)
```

---

## 🎯 Advantages of This Architecture

### ✅ Binary Upload (FormData)
- **Faster**: No base64 encoding overhead
- **Smaller**: ~33% less bandwidth
- **Cleaner**: Direct binary processing

### ✅ CLIP Preprocessing
- **Standardized**: Automatic resize, normalization
- **Robust**: Handles various image formats
- **Optimized**: Uses PyTorch tensors

### ✅ Vector Similarity Search
- **Fast**: O(log n) with HNSW index
- **Accurate**: Cosine similarity on normalized vectors
- **Scalable**: Weaviate Cloud handles millions of vectors

### ✅ RAG Context
- **Relevant**: Only top-k matches used
- **Grounded**: LLM answers based on actual DB data
- **Transparent**: Returns certainty scores

---

## 🚀 Usage Example

### Frontend (React)
```javascript
const formData = new FormData();
formData.append('file', imageFile);  // Binary file
formData.append('message', 'What flower is this?');

const response = await fetch('http://localhost:8000/api/v1/chat-with-image', {
  method: 'POST',
  body: formData  // No JSON, pure binary!
});

const data = await response.json();
console.log(data.response);  // LLM answer
console.log(data.identified_plants);  // Top matches
console.log(data.confidence);  // Similarity score
```

### Backend Response
```json
{
  "session_id": "abc-123-def",
  "response": "This appears to be a Damascus Rose (Rosa damascena), a fragrant species known for...",
  "identified_plants": [
    {
      "scientificName": "Rosa damascena",
      "commonName": "Damascus Rose",
      "_additional": {"certainty": 0.95}
    }
  ],
  "confidence": 0.95,
  "timestamp": "2025-10-18T12:34:56.789Z"
}
```

---

## 🔧 Configuration

### Environment Variables (`.env`)
```bash
# CLIP Model
CLIP_MODEL_NAME=openai/clip-vit-base-patch32

# Weaviate Cloud
WEAVIATE_URL=https://xxx.weaviate.cloud
WEAVIATE_API_KEY=your_api_key

# OpenRouter LLM
OPENROUTER_API_KEY=sk-or-v1-xxx
OPENROUTER_MODEL=nvidia/nemotron-nano-9b-v2:free
```

---

## 📊 Performance Metrics

| Component | Latency | Notes |
|-----------|---------|-------|
| Image upload | ~50ms | FormData binary |
| CLIP encoding | ~200ms | CPU, ~50ms GPU |
| Vector search | ~20ms | Weaviate Cloud |
| LLM generation | ~2s | OpenRouter API |
| **Total** | **~2.3s** | End-to-end |

---

## 🛠️ Future Improvements

1. **Caching**: Redis for frequent queries
2. **Batch Processing**: Multiple images at once
3. **Fine-tuning**: CLIP on plant-specific dataset (PlantCLEF)
4. **Hybrid Search**: Combine vector + keyword search
5. **Streaming**: LLM response streaming for better UX

---

## 📚 References

- **CLIP Paper**: [Learning Transferable Visual Models](https://arxiv.org/abs/2103.00020)
- **Weaviate Docs**: [Vector Search](https://weaviate.io/developers/weaviate/search/similarity)
- **RAG Pattern**: [Retrieval-Augmented Generation for AI](https://arxiv.org/abs/2005.11401)
