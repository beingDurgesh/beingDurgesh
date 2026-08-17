import cv2
import numpy as np
import os, glob

folder = "/Users/mdkasifuddin/.gemini/antigravity-ide/brain/05a83f3c-b6f1-449e-8acd-32367c0fcd40/.tempmediaStorage"
files = glob.glob(f"{folder}/media_*.png")
files.sort(key=os.path.getmtime, reverse=True)

# Try the latest 5 files
for img_path in files[:5]:
    img = cv2.imread(img_path)
    if img is None: continue
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # The dev logo is black on white. Let's threshold it: everything < 200 becomes white (255), white background becomes black (0)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 100 and h > 100:
            ratio = w / h
            if 0.8 < ratio < 1.3:
                print(f"Found square logo in {os.path.basename(img_path)} at {x},{y} size {w}x{h}")
                # Save it!
                logo = img[y:y+h, x:x+w]
                cv2.imwrite("extracted_dev_logo.png", logo)
                exit(0)
                
print("No logo found.")
