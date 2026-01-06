# =============================================================
# 🌿 PLANT RECOGNITION AI - KAGGLE NOTEBOOK
# Bu kodu Kaggle notebook'unuza yapıştırın ve çalıştırın
# =============================================================

# CELL 1: Imports
import os
import json
import torch
import gradio as gr
from PIL import Image
from pathlib import Path
from transformers import CLIPProcessor, CLIPModel

print("✅ Libraries loaded")

# =============================================================
# CELL 2: Load PlantCLEF Dataset Species List
# =============================================================
DATASET_PATH = "/kaggle/input/plantclef2025"

# Build species list from dataset folders
species_list = []
for root, dirs, files in os.walk(DATASET_PATH):
    for dir_name in dirs:
        if dir_name and not dir_name.startswith("."):
            species_list.append(dir_name)
    break  # Only top level

# Limit to first 500 species for memory
species_list = species_list[:500]
print(f"✅ Loaded {len(species_list)} species from PlantCLEF2025")

# =============================================================
# CELL 3: Load CLIP Model
# =============================================================
print("Loading CLIP model...")
device = "cuda" if torch.cuda.is_available() else "cpu"

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
model = model.to(device)
model.eval()

print(f"✅ CLIP loaded on {device}")


# =============================================================
# CELL 4: Plant Identification Function
# =============================================================
def identify_plant(image, top_k=5):
    """
    Identify plant species using CLIP + PlantCLEF dataset

    Args:
        image: PIL Image
        top_k: Number of top predictions

    Returns:
        Dictionary with species names and confidence scores
    """
    if image is None:
        return {"error": "No image provided"}

    try:
        # Convert to PIL if needed
        if not isinstance(image, Image.Image):
            image = Image.fromarray(image)
        image = image.convert("RGB")

        # Create text prompts for each species
        text_prompts = [f"a photo of {species}" for species in species_list]

        # Encode with CLIP
        with torch.no_grad():
            inputs = processor(
                text=text_prompts,
                images=image,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=77,
            ).to(device)

            outputs = model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]

        # Get top predictions
        top_indices = probs.argsort()[::-1][:top_k]

        results = {}
        for idx in top_indices:
            species_name = species_list[idx]
            confidence = float(probs[idx])
            results[species_name] = confidence

        return results

    except Exception as e:
        return {"error": str(e)}


# =============================================================
# CELL 5: API Function for Backend Integration
# =============================================================
def api_predict(image):
    """
    API endpoint function - returns JSON-compatible output
    """
    results = identify_plant(image, top_k=5)

    if "error" in results:
        return json.dumps({"error": results["error"]})

    predictions = []
    for species, confidence in results.items():
        predictions.append(
            {
                "scientificName": species,
                "confidence": confidence,
                "source": "PlantCLEF2025-CLIP",
            }
        )

    return json.dumps(
        {
            "predictions": predictions,
            "model": "CLIP-ViT-B/32",
            "dataset": "PlantCLEF2025",
            "species_count": len(species_list),
        }
    )


# =============================================================
# CELL 6: Create Gradio Interface
# =============================================================
demo = gr.Interface(
    fn=identify_plant,
    inputs=gr.Image(type="pil", label="🌿 Plant Image"),
    outputs=gr.Label(num_top_classes=5, label="🔍 Predictions"),
    title="🌿 Plant Recognition AI",
    description="Upload a plant image to identify the species using PlantCLEF2025 dataset",
    examples=[],
    allow_flagging="never",
)

# Add API endpoint
demo.queue()

# =============================================================
# CELL 7: Launch with Public URL
# =============================================================
print("\n" + "=" * 60)
print("🌿 STARTING PLANT RECOGNITION API...")
print("=" * 60)

demo.launch(
    share=True,  # Creates public URL
    show_error=True,
    server_name="0.0.0.0",
    server_port=7860,
)

# After launch, you'll see:
# Running on public URL: https://xxxxxx.gradio.live
#
# Copy this URL to your .env file:
# KAGGLE_NOTEBOOK_URL=https://xxxxxx.gradio.live
