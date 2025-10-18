import os
import kaggle
from pathlib import Path
from typing import Optional
import zipfile
import shutil

class KaggleService:
    def __init__(self):
        self.dataset_name = "plantclef2025"
        self.base_path = Path("data/kaggle")
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def download_dataset(self, dataset_path: str = "plantclef2025") -> str:
        """Kaggle dataset'ini indir"""
        try:
            download_path = self.base_path / dataset_path
            download_path.mkdir(parents=True, exist_ok=True)
            
            kaggle.api.dataset_download_files(
                dataset_path,
                path=str(download_path),
                unzip=True
            )
            return str(download_path)
        except Exception as e:
            raise Exception(f"Kaggle download error: {str(e)}")
    
    def list_dataset_files(self, dataset_path: Optional[str] = None) -> list:
        """Dataset dosyalarını listele"""
        if not dataset_path:
            dataset_path = self.base_path / self.dataset_name
        
        files = []
        for dirname, _, filenames in os.walk(dataset_path):
            for filename in filenames:
                files.append(os.path.join(dirname, filename))
        return files
    
    def get_plant_images(self, limit: int = 100) -> list:
        """PlantCLEF dataset'inden bitki görsellerini al"""
        dataset_path = self.base_path / self.dataset_name
        if not dataset_path.exists():
            self.download_dataset()
        
        images = []
        for dirname, _, filenames in os.walk(dataset_path):
            for filename in filenames:
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    images.append(os.path.join(dirname, filename))
                    if len(images) >= limit:
                        return images
        return images

kaggle_service = KaggleService()
