from PIL import Image
import pytesseract
from reportlab.pdfgen import canvas
import cv2
import numpy as np
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Adjust for your OS

def preprocess_image(image_path):
    """Load image, convert to grayscale, denoise, and binarize."""
    image = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply denoising
    denoised = cv2.fastNlMeansDenoising(gray, None, h=8, templateWindowSize=7, searchWindowSize=21)

    # Apply binary thresholding
    _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Save the preprocessed image
    cv2.imwrite("output/prepro-img.jpg", binary)

    return image, binary

def image_to_searchable_pdf(image_path, pdf_path):
    original_img, preprocessed_img = preprocess_image(image_path)

    height, width = original_img.shape[:2]

    # Save the original image as RGB for PDF background
    temp_image_path = "temp_image.jpg"
    Image.fromarray(cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)).save(temp_image_path)

    # OCR using preprocessed (binary) image
    pil_preprocessed = Image.fromarray(preprocessed_img)
    data = pytesseract.image_to_data(pil_preprocessed, output_type=pytesseract.Output.DICT)

    # Create PDF canvas matching image size
    c = canvas.Canvas(pdf_path, pagesize=(width, height))

    # Draw original image as background
    c.drawImage(temp_image_path, 0, 0, width=width, height=height)

    # Transparent text layer
    c.setFillColorRGB(1, 1, 1, alpha=0)  # invisible fill
    c.setFont("Helvetica", 10)

    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 60:
            x, y = int(data['left'][i]), int(data['top'][i])
            w, h = int(data['width'][i]), int(data['height'][i])
            text = data['text'][i]
            if text.strip():
                c.drawString(x, height - y - h + 2, text)

    c.save()
    os.remove(temp_image_path)
    print(f"✅ Searchable PDF saved to: {pdf_path}")

if __name__ == "__main__":
    image_to_searchable_pdf("input/cert.jpg", "output/output.pdf")
    print("Searchable PDF created!")