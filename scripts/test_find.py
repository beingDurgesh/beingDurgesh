import os, glob
from PIL import Image, ImageOps

folder = "/Users/mdkasifuddin/.gemini/antigravity-ide/brain/05a83f3c-b6f1-449e-8acd-32367c0fcd40/.tempmediaStorage"
files = sorted(glob.glob(f"{folder}/media_*.png"), key=os.path.getmtime, reverse=True)

for i, img_path in enumerate(files[:6]):
    try:
        img = Image.open(img_path).convert("RGBA")
        
        # Check if it has a transparent background
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        bg.paste(img, (0, 0), img)
        gray = bg.convert("L")
        inv = ImageOps.invert(gray)
        bbox = inv.getbbox()
        
        print(f"Index {i}: {os.path.basename(img_path)} - size {img.size} - bbox {bbox}")
    except Exception as e:
        print(f"Index {i}: {e}")
