import sys
from PIL import Image

for i in range(1, 5):
    img_path = f"img{i}.png"
    try:
        img = Image.open(img_path)
        print(f"{img_path}: format={img.format}, size={img.size}, mode={img.mode}")
    except Exception as e:
        print(f"{img_path}: {e}")
