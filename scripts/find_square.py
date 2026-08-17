import os, glob
from PIL import Image, ImageOps

folder = "/Users/mdkasifuddin/.gemini/antigravity-ide/brain/05a83f3c-b6f1-449e-8acd-32367c0fcd40/.tempmediaStorage"
files = glob.glob(f"{folder}/media_*.png")
files.sort(key=os.path.getmtime, reverse=True)

for img_path in files:
    try:
        img = Image.open(img_path).convert("RGBA")
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        bg.paste(img, (0, 0), img)
        gray = bg.convert("L")
        inv = ImageOps.invert(gray)
        bbox = inv.getbbox()
        
        if bbox:
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            ratio = w / h
            # if ratio is close to 1
            if 0.8 < ratio < 1.2:
                print(f"SQUARE FOUND! {os.path.basename(img_path)} | size: {img.size} | bbox: {w}x{h} | ratio: {ratio:.2f}")
    except:
        pass
