import sys
from PIL import Image, ImageEnhance, ImageOps
import os

OUTPUT_DIR = "."

def process(name):
    icon_path = os.path.join(OUTPUT_DIR, name)
    img = Image.open(icon_path).convert("RGBA")
    
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    bg.paste(img, (0, 0), img)
    img = bg.convert("L")
    img.thumbnail((400, 400), Image.LANCZOS)
    
    final_img = Image.new("L", (400, 400), 255)
    offset = ((400 - img.width) // 2, (400 - img.height) // 2)
    final_img.paste(img, offset)
    
    final_img = ImageEnhance.Contrast(final_img).enhance(2.0)
    
    # Simulate stipple dots
    final_img = final_img.resize((320, 360), Image.LANCZOS)
    pixels = final_img.load()
    dark_pixels = 0
    weights = []
    for y in range(360):
        for x in range(320):
            darkness = 255 - pixels[x, y]
            if darkness > 20:
                dark_pixels += 1
                weights.append(darkness)
    
    print(f"{name}: {final_img.size}, Dark pixels: {dark_pixels}, sum_weights: {sum(weights) if weights else 0}")
    
process("dev-icon-source.png")
process("python-icon-source.png")
