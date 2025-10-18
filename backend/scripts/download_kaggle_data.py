"""
Download Kaggle PlantCLEF 2025 dataset
Note: This is a very large dataset (~100GB+)
"""
from kaggle.api.kaggle_api_extended import KaggleApi
from pathlib import Path

def download_plantclef_dataset():
    api = KaggleApi()
    api.authenticate()
    
    download_path = Path("data/kaggle/plantclef2025")
    download_path.mkdir(parents=True, exist_ok=True)
    
    print("Downloading PlantCLEF 2025 dataset...")
    print("WARNING: This is a very large dataset (~100GB+)")
    
    try:
        api.dataset_download_files(
            'plantclef2025',
            path=str(download_path),
            unzip=True
        )
        print("Dataset downloaded successfully!")
        print(f"Location: {download_path.absolute()}")
        
        files = list(download_path.rglob("*"))
        print(f"Total files: {len(files)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nSolutions:")
        print("1. Check Kaggle credentials: ~/.kaggle/kaggle.json")
        print("2. Verify dataset name: kaggle datasets list -s plant")
        print("3. Manual download: https://www.kaggle.com/datasets/plantclef2025")

if __name__ == "__main__":
    download_plantclef_dataset()
