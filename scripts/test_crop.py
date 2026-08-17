import sys
from PIL import Image, ImageEnhance, ImageOps
import os

def process_cropped(name):
    icon_path = name
    if not os.path.exists(icon_path):
        return
    img = Image.open(icon_path).convert("RGBA")
    
    # Create white background to safely find bounding box
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    bg.paste(img, (0, 0), img)
    
    gray = bg.convert("L")
    inv = ImageOps.invert(gray)
    bbox = inv.getbbox()
    
    if bbox:
        # Crop to the actual content
        bg = bg.crop(bbox)
    
    # Convert to grayscale
    img = bg.convert("L")
    
    # Resize to fit within size bounds, but let's make it 320x320 max so it fits in 400x400 with padding
    img.thumbnail((320, 320), Image.LANCZOS)
    
    # Center on white canvas
    final_img = Image.new("L", (400, 400), 255)
    offset = ((400 - img.width) // 2, (400 - img.height) // 2)
    final_img.paste(img, offset)
    
    final_img = ImageEnhance.Contrast(final_img).enhance(2.0)
    
    # Simulate stipple
    final_img = final_img.resize((320, 360), Image.LANCZOS)
    pixels = final_img.load()
    dark_pixels = 0
    for y in range(360):
        for x in range(320):
            if 255 - pixels[x, y] > 20:
                dark_pixels += 1
                
    print(f"{name}: cropped size {bbox}, resized content {img.size}, dark pixels {dark_pixels}")

process_cropped("dev-icon-source.png")
process_cropped("python-icon-source.png")
