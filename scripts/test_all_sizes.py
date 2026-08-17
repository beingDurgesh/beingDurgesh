import os, glob
from PIL import Image

folder = "/Users/mdkasifuddin/.gemini/antigravity-ide/brain/05a83f3c-b6f1-449e-8acd-32367c0fcd40/.tempmediaStorage"
files = glob.glob(f"{folder}/media_*.png")
sizes = set()

for img_path in files:
    try:
        img = Image.open(img_path)
        sizes.add(img.size)
    except:
        pass

print("Unique sizes in tempmediaStorage:")
for size in sizes:
    print(size)
