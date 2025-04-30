from PIL import Image
import pytesseract
from reportlab.pdfgen import canvas
import cv2
import numpy as np
import os
import layoutparser as lp

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Adjust if needed

def preprocess_image(image_path):
    image = cv2.imread(image_path)

    # # Upscale image (can help OCR read finer text better)
    # image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # Gentle denoising
    denoised = cv2.fastNlMeansDenoisingColored(image, None, 5, 10, 7, 21)

    # Convert to LAB and enhance contrast
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    merged = cv2.merge((cl, a, b))
    enhanced = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)

    # # Sharpening (can help bring back faint edges)
    # kernel = np.array([[0, -1, 0],
    #                    [-1, 5,-1],
    #                    [0, -1, 0]])
    # sharpened = cv2.filter2D(enhanced, -1, kernel)

    # Threshold to detect skew
    gray_for_thresh = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray_for_thresh, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    angle = -(90 + angle) if angle < -45 else -angle

    (h, w) = image.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    aligned_image = cv2.warpAffine(enhanced, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    os.makedirs("output", exist_ok=True)
    cv2.imwrite("output/exp/hyper/new-prepro-img.jpg", aligned_image)

    return image, aligned_image


def image_to_searchable_pdf(image_path, pdf_path):
    original_img, preprocessed_img = preprocess_image(image_path)

    height, width = original_img.shape[:2]

    # Save original image as RGB for the PDF background
    temp_image_path = "temp_image.jpg"
    Image.fromarray(cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)).save(temp_image_path)

    # Use Tesseract to extract layout-aware data
    custom_config = r'--oem 3 --psm 12 -l eng'
    pil_image = Image.fromarray(preprocessed_img)
    data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT, config=custom_config)

    # Create canvas with same size as image
    c = canvas.Canvas(pdf_path, pagesize=(width, height))
    c.drawImage(temp_image_path, 0, 0, width=width, height=height)

    # Transparent text overlay
    c.setFillColorRGB(1, 1, 1, alpha=0)
    c.setFont("Helvetica", 10)

    # Group words by line
    lines = {}
    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 60 and data['text'][i].strip():
            key = (data['block_num'][i], data['par_num'][i], data['line_num'][i])
            if key not in lines:
                lines[key] = []
            lines[key].append(i)

    for key in lines:
        word_indices = lines[key]
        line_text = " ".join([data['text'][i] for i in word_indices])
        x = min([data['left'][i] for i in word_indices])
        y = min([data['top'][i] for i in word_indices])
        h = max([data['height'][i] for i in word_indices])
        c.drawString(x, height - y - h + 2, line_text)

    c.save()
    os.remove(temp_image_path)
    print(f"✅ Searchable PDF saved to: {pdf_path}")

if __name__ == "__main__":
    image_to_searchable_pdf("input/cert.jpg", "output/exp/hyper/new-output.pdf")
    print("Searchable PDF created!")
