import os

folder_path = "dataset/raw/Cattle Breeds/Brown Swiss cattle"

images = [
    file for file in os.listdir(folder_path)
    if file.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
]

print("Total images:", len(images))