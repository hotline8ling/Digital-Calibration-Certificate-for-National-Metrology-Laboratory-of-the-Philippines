# Tesseract source: https://github.com/tesseract-ocr/tesseract/releases/tag/5.5.0

from PIL import Image
import pytesseract
from reportlab.pdfgen import canvas
import cv2
import numpy as np
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    os.makedirs("output", exist_ok=True)
    cv2.imwrite("output/prepro-img.jpg", thresh)
    return image, thresh

def run_ocr(image, config):
    pil_image = Image.fromarray(image)
    return pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT, config=config)

def image_to_searchable_pdf(image_path, pdf_path):
    original_img, preprocessed_img = preprocess_image(image_path)
    height, width = original_img.shape[:2]
    temp_image_path = "temp_image.jpg"
    Image.fromarray(cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)).save(temp_image_path)

    # Run OCR for table (sparse layout)
    data_table = run_ocr(preprocessed_img, r'--oem 3 --psm 12')

    # Run OCR for paragraph (block of text)
    data_para = run_ocr(preprocessed_img, r'--oem 3 --psm 4')

    c = canvas.Canvas(pdf_path, pagesize=(width, height))
    c.drawImage(temp_image_path, 0, 0, width=width, height=height)
    c.setFillColorRGB(1, 1, 1, alpha=0)
    c.setFont("Helvetica", 10)
    padding = 2

    def draw_ocr_data(data):
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 60:
                x = int(data['left'][i]) - padding
                y = int(data['top'][i]) - padding
                w = int(data['width'][i]) + 2 * padding
                h = int(data['height'][i]) + 2 * padding
                text = data['text'][i].strip()
                if text:
                    c.drawString(x, height - y - h + 2, text)

    draw_ocr_data(data_table)  # Table
    draw_ocr_data(data_para)   # Paragraph

    c.save()
    os.remove(temp_image_path)
    print(f"✅ Searchable PDF saved to: {pdf_path}")

if __name__ == "__main__":
    image_to_searchable_pdf("input/cert.jpg", "output/final-output.pdf")
    print("Searchable PDF created!")
