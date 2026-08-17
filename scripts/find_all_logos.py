import os, glob
from PIL import Image, ImageOps

folder = "/Users/mdkasifuddin/.gemini/antigravity-ide/brain/05a83f3c-b6f1-449e-8acd-32367c0fcd40/.tempmediaStorage"
files = glob.glob(f"{folder}/media_*.png")

for img_path in files:
    try:
        img = Image.open(img_path).convert("L")
        inv = ImageOps.invert(img)
        # Threshold: > 50 means < 205 in original
        thresh = inv.point(lambda p: 255 if p > 50 else 0)
        bbox = thresh.getbbox()
        
        if bbox:
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            ratio = w / h
            if 0.8 < ratio < 1.3:
                print(f"SQUARE MATCH! {os.path.basename(img_path)} | bbox: {bbox} | {w}x{h} | ratio: {ratio:.2f}")
    except Exception as e:
        pass
