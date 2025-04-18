from PIL import Image
import pytesseract
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Change if needed

def image_to_searchable_pdf(image_path, pdf_path):
    image = Image.open(image_path)
    width, height = image.size

    # Save the image as a temporary image for the PDF background
    image_rgb_path = "temp_image.jpg"
    image.convert("RGB").save(image_rgb_path)

    # Start a canvas with size matching the image
    c = canvas.Canvas(pdf_path, pagesize=(width, height))

    # Draw the image as the background
    c.drawImage(image_rgb_path, 0, 0, width=width, height=height)

    # OCR with bounding boxes
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

    # # Draw bounding boxes on the canvas
    # c.setStrokeColorRGB(1, 0, 0)  # Red color for bounding boxes
    # c.setLineWidth(1)  # Line thickness for bounding boxes

    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 60:  # Confidence filter
            x = int(data['left'][i])
            y = int(data['top'][i])
            w = int(data['width'][i])
            h = int(data['height'][i])
    #         c.rect(x, height - y - h, w, h)  # Draw rectangle

    # c.setFillColorRGB(1, 1, 1, alpha=0)  # Transparent white
    # c.setStrokeColorRGB(1, 1, 1, alpha=0)  # Transparent stroke
    # c.setFont("Helvetica", 10)

    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 60:  # Confidence filter
            x = int(data['left'][i])
            y = int(data['top'][i])
            w = int(data['width'][i])
            h = int(data['height'][i])
            text = data['text'][i]
            if text.strip():
                c.drawString(x, height - y - h + 2, text)  # y-coord correction

    c.save()
    os.remove(image_rgb_path)

if __name__ == "__main__":
    image_to_searchable_pdf("input/cert.jpg", "output.pdf")
    print("Searchable PDF created!")
