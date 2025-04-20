# Tesseract source: https://github.com/tesseract-ocr/tesseract/releases/tag/5.5.0

from PIL import Image
import pytesseract
from reportlab.pdfgen import canvas
import cv2
import numpy as np
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Adjust if needed

def preprocess_image(image_path):
    """Enhance image contrast and rotate it so it's slightly to the left."""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 5, 7, 21)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    angle = -(90 + angle) if angle < -45 else -angle

    # angle += 1  # Rotate slightly to the left

    (h, w) = image.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    aligned_image = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    aligned_thresh = cv2.warpAffine(thresh, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    os.makedirs("output", exist_ok=True)
    cv2.imwrite("output/exp/new-prepro-img.jpg", aligned_thresh)

    return image, aligned_thresh

def image_to_searchable_pdf(image_path, pdf_path):
    original_img, preprocessed_img = preprocess_image(image_path)

    height, width = original_img.shape[:2]

    # Save original image as RGB for the PDF background
    temp_image_path = "temp_image.jpg"
    Image.fromarray(cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)).save(temp_image_path)

    # OCR config: more accurate with structured layouts
    custom_config = r'--oem 3 --psm 12'

    # Convert image to PIL for pytesseract
    pil_preprocessed = Image.fromarray(preprocessed_img)
    data = pytesseract.image_to_data(pil_preprocessed, output_type=pytesseract.Output.DICT, config=custom_config)

    # Create canvas with the same dimensions as the image
    c = canvas.Canvas(pdf_path, pagesize=(width, height))

    # Draw background image
    c.drawImage(temp_image_path, 0, 0, width=width, height=height)

    # Invisible text overlay for selection/search
    c.setFillColorRGB(1, 1, 1, alpha=0)
    c.setFont("Helvetica", 10)

    padding = 2  # Pixels to expand around each bounding box

    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 60:
            x = int(data['left'][i]) - padding
            y = int(data['top'][i]) - padding
            w = int(data['width'][i]) + 2 * padding
            h = int(data['height'][i]) + 2 * padding
            text = data['text'][i].strip()
            if text:
                c.drawString(x, height - y - h + 2, text)

    c.save()
    os.remove(temp_image_path)
    print(f"✅ Searchable PDF saved to: {pdf_path}")

if __name__ == "__main__":
    image_to_searchable_pdf("input/cert.jpg", "output/exp/new-output.pdf")
    print("Searchable PDF created!")
