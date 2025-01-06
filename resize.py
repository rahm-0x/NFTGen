import os
from PIL import Image

# Base directory
base_dir = "/Users/phoenix/Desktop/pythonscripts/nft-generator-py/trait-layers"

# Target size (3500x3500 to match larger images)
TARGET_SIZE = (3500, 3500)

# Resize images
def resize_images(base_dir, target_size):
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".png"):
                path = os.path.join(root, file)
                img = Image.open(path)
                
                # Resize only if dimensions do not match
                if img.size != target_size:
                    print(f"Resizing: {path} | Original Size: {img.size}")
                    img = img.resize(target_size, Image.Resampling.LANCZOS)
                    img.save(path)
                    print(f"✅ Resized and saved: {path}")
                else:
                    print(f"Skipping (Already Correct): {path}")

# Run the resizing
resize_images(base_dir, TARGET_SIZE)
print("🎉 All images have been resized successfully!")
