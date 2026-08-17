import os, glob
from PIL import Image

folder = "/Users/mdkasifuddin/.gemini/antigravity-ide/brain/05a83f3c-b6f1-449e-8acd-32367c0fcd40/.tempmediaStorage"
files = glob.glob(f"{folder}/media_*.png")
files.sort(key=os.path.getmtime, reverse=True)

for img_path in files[:10]:
    try:
        img = Image.open(img_path).convert("RGBA")
        
        # Check alpha channel directly!
        alpha = img.split()[3]
        bbox = alpha.getbbox()
        
        if bbox:
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            ratio = w / h
            print(f"{os.path.basename(img_path)} | size: {img.size} | alpha bbox: {w}x{h} | ratio: {ratio:.2f}")
        else:
            print(f"{os.path.basename(img_path)} | NO ALPHA BBOX (fully transparent?)")
            
    except Exception as e:
        pass
