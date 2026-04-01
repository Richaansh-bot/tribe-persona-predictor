"""Download TRIBE v2 model"""

from tribev2 import TribeModel

print("Downloading TRIBE v2 model from HuggingFace...")
print("This may take a few minutes depending on your connection...")

model = TribeModel.from_pretrained("facebook/tribev2", cache_folder="./cache")

print("TRIBE v2 model downloaded successfully!")
print(f"Model location: ./cache")
