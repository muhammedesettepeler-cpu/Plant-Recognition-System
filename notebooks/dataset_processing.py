# Dataset Processing for Plant Images
import pandas as pd
from pathlib import Path

DATA_DIR = Path("../data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

print("Plant Dataset Processing")
print(f"Raw: {RAW_DIR}")
print(f"Processed: {PROCESSED_DIR}")

# TODO: Add your dataset processing here
# 1. Load images from Kaggle
# 2. Generate CLIP embeddings
# 3. Store in Weaviate
# 4. Save metadata to PostgreSQL
