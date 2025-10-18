# System Architecture & Data Flow

## 🏗️ System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Home Page   │  │ Recognition  │  │   Chatbot    │         │
│  │              │  │    Page      │  │    Page      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│         React.js + Material-UI Frontend (Port 3000)            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTP/REST API
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                            │
│                       (Port 8000)                               │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    API LAYER                            │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐               │   │
│  │  │  Health  │ │  Recog.  │ │ Chatbot  │               │   │
│  │  │    API   │ │   API    │ │   API    │               │   │
│  │  └──────────┘ └──────────┘ └──────────┘               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 SERVICE LAYER                           │   │
│  │                                                         │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │   │
│  │  │ CLIP Service │  │  Weaviate    │  │    Grok     │  │   │
│  │  │ (Embeddings) │  │   Service    │  │   Service   │  │   │
│  │  │              │  │  (Vectors)   │  │    (LLM)    │  │   │
│  │  └──────────────┘  └──────────────┘  └─────────────┘  │   │
│  │                                                         │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │   │
│  │  │  PlantNet    │  │     USDA     │  │   IDrive    │  │   │
│  │  │   Service    │  │   Service    │  │   Storage   │  │   │
│  │  │              │  │              │  │             │  │   │
│  │  └──────────────┘  └──────────────┘  └─────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────┬──────────────────────┬──────────────────────┘
                    │                      │
        ┌───────────┴─────────┐   ┌────────┴─────────┐
        ▼                     ▼   ▼                  ▼
┌───────────────┐    ┌──────────────────┐    ┌──────────────┐
│  PostgreSQL   │    │    Weaviate      │    │  External    │
│  (Metadata)   │    │  Vector Store    │    │     APIs     │
│   Port 5432   │    │   Port 8080      │    │              │
└───────────────┘    └──────────────────┘    │ - PlantNet   │
                                             │ - Grok       │
                                             │ - USDA       │
                                             │ - IDrive e2  │
                                             └──────────────┘
```

## 📊 Data Flow Diagrams

### 1. Image Recognition Flow

```
User Upload Image
        │
        ▼
┌───────────────┐
│   Frontend    │
│  (React UI)   │
└───────┬───────┘
        │ POST /api/v1/recognize
        │ (multipart/form-data)
        ▼
┌───────────────────────────────────┐
│     FastAPI Backend               │
│                                   │
│  1. Validate Image                │
│  2. Process Image (OpenCV)        │
│     ├─ Enhance quality            │
│     └─ Extract plant region       │
└───────┬───────────────────────────┘
        │
        ├──────────────┬──────────────┬─────────────┐
        ▼              ▼              ▼             ▼
┌─────────────┐ ┌──────────┐  ┌──────────┐  ┌────────────┐
│  PlantNet   │ │   CLIP   │  │ Weaviate │  │    Grok    │
│  API Call   │ │ Generate │  │Similarity│  │ Generate   │
│             │ │Embedding │  │  Search  │  │Description │
└──────┬──────┘ └────┬─────┘  └────┬─────┘  └─────┬──────┘
       │             │              │              │
       └─────────────┴──────────────┴──────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  Combine Results        │
        │  - Top match            │
        │  - Confidence score     │
        │  - Scientific name      │
        │  - Description (LLM)    │
        └───────────┬─────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  Return JSON Response │
        │  to Frontend          │
        └───────────────────────┘
```

### 2. Chatbot Interaction Flow

```
User Message Input
        │
        ▼
┌───────────────┐
│   Frontend    │
│  (Chat UI)    │
└───────┬───────┘
        │ POST /api/v1/chat
        │ {message, session_id, history}
        ▼
┌───────────────────────────────────┐
│     FastAPI Backend               │
│                                   │
│  1. Analyze Query                 │
│  2. Check if plant-related        │
└───────┬───────────────────────────┘
        │
        ▼
    Is Plant Query?
        │
    ┌───┴───┐
    │  YES  │ NO
    ▼       │
┌─────────────┐   │
│    CLIP     │   │
│  Text       │   │
│ Embedding   │   │
└──────┬──────┘   │
       │          │
       ▼          │
┌─────────────┐   │
│  Weaviate   │   │
│  Similarity │   │
│   Search    │   │
│             │   │
│ Retrieve    │   │
│  Top 3-5    │   │
│  Plants     │   │
└──────┬──────┘   │
       │          │
       └──────┬───┘
              ▼
     ┌──────────────────┐
     │   Grok LLM API   │
     │                  │
     │  RAG Process:    │
     │  - Context       │
     │  - History       │
     │  - Retrieved     │
     │    Plants        │
     └────────┬─────────┘
              │
              ▼
     ┌────────────────────┐
     │  Natural Language  │
     │     Response       │
     └─────────┬──────────┘
               │
               ▼
     ┌─────────────────────┐
     │  Save to Database   │
     │  (UserQuery table)  │
     └──────────┬──────────┘
                │
                ▼
     ┌──────────────────────┐
     │  Return to Frontend  │
     │  with:               │
     │  - Response text     │
     │  - Related plants    │
     │  - Timestamp         │
     └──────────────────────┘
```

### 3. Vector Embedding & Storage Flow

```
Plant Image Dataset (Kaggle)
        │
        ▼
┌─────────────────────┐
│  Data Processing    │
│  (Jupyter Notebook) │
│                     │
│  - Load images      │
│  - Preprocess       │
│  - Resize/normalize │
└──────────┬──────────┘
           │
           ▼
    ┌─────────────┐
    │ CLIP Model  │
    │             │
    │ Generate    │
    │ 512-dim     │
    │ Embeddings  │
    └──────┬──────┘
           │
    ┌──────┴──────┐
    ▼             ▼
┌────────┐  ┌──────────────┐
│Weaviate│  │  PostgreSQL  │
│        │  │              │
│Vector  │  │  Metadata:   │
│Store   │  │  - sci_name  │
│        │  │  - common    │
│512-dim │  │  - family    │
│vectors │  │  - habitat   │
│        │  │  - care      │
└────────┘  └──────────────┘
```

## 🔄 RAG (Retrieval-Augmented Generation) Process

```
User Query: "What plants need full sun?"
                │
                ▼
        ┌───────────────┐
        │ Text → Vector │
        │  (CLIP Text)  │
        └───────┬───────┘
                │
                ▼
        ┌───────────────────┐
        │ Similarity Search │
        │   in Weaviate     │
        │                   │
        │ Find K=5 nearest  │
        │   neighbors       │
        └─────────┬─────────┘
                  │
                  ▼
        Retrieved Plants:
        1. Sunflower (0.92)
        2. Lavender (0.89)
        3. Rose (0.87)
        4. Tomato (0.85)
        5. Marigold (0.83)
                  │
                  ▼
        ┌─────────────────────┐
        │  Build RAG Context  │
        │                     │
        │  Retrieved Info:    │
        │  + Plant names      │
        │  + Descriptions     │
        │  + Care info        │
        │  + Metadata         │
        └──────────┬──────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Prompt Engineering  │
        │                      │
        │  System: "You are a │
        │  botanist. Context: │
        │  [Retrieved plants]" │
        │                      │
        │  User: [Query]       │
        └───────────┬──────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │      Grok LLM         │
        │                       │
        │  Generate coherent    │
        │  natural language     │
        │  response based on    │
        │  context + query      │
        └────────────┬──────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  Final Response:       │
        │                        │
        │  "Several plants thrive│
        │  in full sun including │
        │  Sunflower, Lavender,  │
        │  and Roses. They need  │
        │  at least 6-8 hours of │
        │  direct sunlight..."   │
        └────────────────────────┘
```

## 🗄️ Database Schema

### PostgreSQL Tables

```
┌─────────────────────────────────┐
│          plants                 │
├─────────────────────────────────┤
│ id (PK)            INTEGER      │
│ scientific_name    VARCHAR(255) │
│ common_name        VARCHAR(255) │
│ family             VARCHAR(100) │
│ genus              VARCHAR(100) │
│ species            VARCHAR(100) │
│ description        TEXT         │
│ characteristics    JSON         │
│ habitat            TEXT         │
│ native_region      VARCHAR(255) │
│ care_instructions  TEXT         │
│ water_requirements VARCHAR(50)  │
│ sunlight_req       VARCHAR(50)  │
│ soil_type          VARCHAR(100) │
│ toxicity           VARCHAR(100) │
│ uses               TEXT         │
│ usda_id            VARCHAR(100) │
│ plantnet_id        VARCHAR(100) │
│ image_urls         JSON         │
│ weaviate_id        VARCHAR(255) │
│ created_at         TIMESTAMP    │
│ updated_at         TIMESTAMP    │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│        user_queries             │
├─────────────────────────────────┤
│ id (PK)            INTEGER      │
│ session_id         VARCHAR(255) │
│ query_type         VARCHAR(50)  │
│ query_text         TEXT         │
│ image_url          VARCHAR(500) │
│ identified_plant_id INTEGER     │
│ confidence_score   FLOAT        │
│ response           TEXT         │
│ created_at         TIMESTAMP    │
└─────────────────────────────────┘
```

### Weaviate Schema

```
Class: PlantImage
├─ Properties:
│  ├─ plantId (int)
│  ├─ scientificName (text)
│  ├─ commonName (text)
│  ├─ imageUrl (text)
│  ├─ imageHash (text)
│  └─ metadata (text/json)
└─ Vector: [512 dimensions from CLIP]
```

## 🌐 Technology Stack Overview

```
┌──────────────────────────────────────┐
│         PRESENTATION LAYER           │
│  React.js + Material-UI + Axios      │
└───────────────┬──────────────────────┘
                │
┌───────────────┴──────────────────────┐
│         APPLICATION LAYER            │
│  FastAPI + Uvicorn + Pydantic        │
└───────────────┬──────────────────────┘
                │
┌───────────────┴──────────────────────┐
│          SERVICE LAYER               │
│  ┌────────────┐  ┌────────────────┐  │
│  │ AI/ML      │  │ External APIs  │  │
│  │ - CLIP     │  │ - PlantNet     │  │
│  │ - OpenCV   │  │ - Grok         │  │
│  │ - TF       │  │ - USDA         │  │
│  └────────────┘  └────────────────┘  │
└───────────────┬──────────────────────┘
                │
┌───────────────┴──────────────────────┐
│          DATA LAYER                  │
│  PostgreSQL + Weaviate + IDrive      │
└──────────────────────────────────────┘
```

---

**This document provides visual representation of the system architecture and data flows.**
