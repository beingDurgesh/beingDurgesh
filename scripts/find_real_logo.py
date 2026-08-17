import os, glob
from PIL import Image, ImageOps

folder = "/Users/mdkasifuddin/.gemini/antigravity-ide/brain/05a83f3c-b6f1-449e-8acd-32367c0fcd40/.tempmediaStorage"
files = glob.glob(f"{folder}/media_*.png")
files.sort(key=os.path.getmtime, reverse=True)

for img_path in files[:10]:
    try:
        img = Image.open(img_path).convert("L")
        
        # Invert so white background becomes black, black lines become white
        inv = ImageOps.invert(img)
        
        # Get bounding box of white pixels (the logo)
        # We might need to threshold it if it's not perfectly white
        # Let's threshold it: any pixel > 50 in inverted (means < 205 in original) becomes 255
        thresh = inv.point(lambda p: 255 if p > 50 else 0)
        
        bbox = thresh.getbbox()
        
        if bbox:
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            ratio = w / h
            print(f"{os.path.basename(img_path)} | bbox: {bbox} | w: {w}, h: {h} | ratio: {ratio:.2f}")
    except Exception as e:
        pass
