import os, glob
from PIL import Image, ImageOps

folder = "/Users/mdkasifuddin/.gemini/antigravity-ide/brain/05a83f3c-b6f1-449e-8acd-32367c0fcd40/.tempmediaStorage"
files = glob.glob(f"{folder}/media_*.png")

results = []
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
            results.append((os.path.basename(img_path), os.path.getmtime(img_path), img.size, w, h, ratio))
    except:
        pass

# Sort by modification time
results.sort(key=lambda x: x[1], reverse=True)

for r in results[:15]:
    print(f"{r[0]} | size: {r[2]} | bbox: {r[3]}x{r[4]} | ratio: {r[5]:.2f}")
