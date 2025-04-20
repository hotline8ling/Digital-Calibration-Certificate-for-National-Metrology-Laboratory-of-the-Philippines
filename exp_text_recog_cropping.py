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
    denoised = cv2.fastNlMeansDenoising(gray, None, 5, 7, 21)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    angle = -(90 + angle) if angle < -45 else -angle

    (h, w) = image.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    aligned_image = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    aligned_thresh = cv2.warpAffine(thresh, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return aligned_image, aligned_thresh

def detect_sections(binary_img, min_gap_height=40):
    height, width = binary_img.shape
    projection = np.sum(binary_img == 255, axis=1)
    white_rows = projection > (0.98 * width)

    gaps = []
    start = None
    for i, is_white in enumerate(white_rows):
        if is_white and start is None:
            start = i
        elif not is_white and start is not None:
            if i - start >= min_gap_height:
                gaps.append((start, i))
            start = None

    sections = []
    last = 0
    for gap_start, gap_end in gaps:
        sections.append((last, gap_start))
        last = gap_end
    sections.append((last, height))
    return sections

def image_to_searchable_pdf(image_path, pdf_path):
    original_img, preprocessed_img = preprocess_image(image_path)
    height, width = original_img.shape[:2]

    temp_image_path = "temp_image.jpg"
    Image.fromarray(cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)).save(temp_image_path)

    # Use psm 12 as default, but may vary by section later
    custom_config = r'--oem 3 --psm 12'

    pil_preprocessed = Image.fromarray(preprocessed_img)
    data = pytesseract.image_to_data(pil_preprocessed, output_type=pytesseract.Output.DICT, config=custom_config)

    # Section detection
    sections = detect_sections(preprocessed_img)

    # Draw section debug visualization
    debug_img = original_img.copy()
    for idx, (start_y, end_y) in enumerate(sections):
        cv2.rectangle(debug_img, (0, start_y), (width - 1, end_y), (0, 255, 0), 2)
        cv2.putText(debug_img, f"Section {idx+1}", (10, start_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    os.makedirs("output", exist_ok=True)
    cv2.imwrite("output/crop/sectioned.jpg", debug_img)

    # Begin writing PDF
    c = canvas.Canvas(pdf_path, pagesize=(width, height))
    c.drawImage(temp_image_path, 0, 0, width=width, height=height)

    c.setFillColorRGB(1, 1, 1, alpha=0)
    c.setFont("Helvetica", 10)
    padding = 2

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
    print("📸 Debug image saved as output/crop/sectioned.jpg")

if __name__ == "__main__":
    image_to_searchable_pdf("input/cert.jpg", "output/crop/final-output.pdf")
