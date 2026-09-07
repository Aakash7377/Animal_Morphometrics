import os
import random
import shutil

# Source folder containing 300 images
source_folder = "dataset/cleaned/tharparkar"

# Destination folder
destination_folder = "dataset/test/tharparkar"

# Create destination folder if it doesn't exist
os.makedirs(destination_folder, exist_ok=True)

# Get all image files
images = [
    file for file in os.listdir(source_folder)
    if file.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
]

# Randomly select 60 images
selected_images = random.sample(images, 30)

# Copy selected images
for image in selected_images:
    source_path = os.path.join(source_folder, image)
    destination_path = os.path.join(destination_folder, image)

    shutil.copy2(source_path, destination_path)

print(f"Successfully copied {len(selected_images)} random images.")