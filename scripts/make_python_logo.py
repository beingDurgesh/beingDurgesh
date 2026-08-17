from PIL import Image, ImageDraw

def draw_python(size=400):
    img = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    c = size // 2
    s = size // 5
    
    # Top shape (blue)
    draw.pieslice([c-s, c-s*1.5, c+s, c+s*0.5], 180, 0, fill=(0,0,0,255))
    draw.rectangle([c, c-s*1.5, c+s, c], fill=(0,0,0,255))
    draw.rectangle([c-s*1.5, c, c+s, c+s], fill=(0,0,0,255))
    draw.pieslice([c-s*1.5, c, c-s*0.5, c+s], 90, 270, fill=(0,0,0,255))
    
    # Bottom shape (yellow)
    draw.pieslice([c-s, c-s*0.5, c+s, c+s*1.5], 0, 180, fill=(0,0,0,255))
    draw.rectangle([c-s, c, c, c+s*1.5], fill=(0,0,0,255))
    draw.rectangle([c-s, c-s, c+s*1.5, c], fill=(0,0,0,255))
    draw.pieslice([c+s*0.5, c-s, c+s*1.5, c], 270, 90, fill=(0,0,0,255))
    
    # Eyes
    draw.ellipse([c-s*0.3, c-s*1.2, c-s*0.1, c-s*1.0], fill=(255,255,255,255))
    draw.ellipse([c+s*0.1, c+s*1.0, c+s*0.3, c+s*1.2], fill=(255,255,255,255))
    
    img.save("python-icon-source.png")

draw_python()
