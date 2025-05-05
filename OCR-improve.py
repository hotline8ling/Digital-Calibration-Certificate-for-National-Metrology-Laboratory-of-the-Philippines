# Tesseract source: https://github.com/tesseract-ocr/tesseract/releases/tag/5.5.0

from PIL import Image
import pytesseract
from reportlab.pdfgen import canvas
import cv2
import numpy as np
import os
import datetime

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image_path):
    image = cv2.imread(image_path)

    # 1) Gentle denoising
    denoised = cv2.fastNlMeansDenoisingColored(image, None, 5, 10, 7, 21)

    # 2) Convert to LAB, apply CLAHE on L-channel
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)

    # 3) Unsharp mask on the L-channel for light sharpening
    #    (blur L, then add a fraction back)
    blur = cv2.GaussianBlur(cl, (5,5), sigmaX=1.0)
    sharp_l = cv2.addWeighted(cl, 1.3, blur, -0.3, 0)

    # 4) Merge back and convert to BGR
    merged = cv2.merge((sharp_l, a, b))
    enhanced = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)

    # Save for inspection
    os.makedirs("output/", exist_ok=True)
    # cv2.imwrite("output/new-prepro-img.jpg", enhanced)
    # print("✅ Preprocessed image saved to: output/new-prepro-img.jpg")

    return image, enhanced


def detect_cells(image, min_cell_area=100, grid_divisor=50):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    bw = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                               cv2.THRESH_BINARY, 15, -2)
    horizontal = bw.copy()
    vertical = bw.copy()
    h_size = max(1, int(horizontal.shape[1] / grid_divisor))
    v_size = max(1, int(vertical.shape[0] / grid_divisor))
    h_struct = cv2.getStructuringElement(cv2.MORPH_RECT, (h_size, 1))
    v_struct = cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_size))
    horizontal = cv2.erode(horizontal, h_struct)
    horizontal = cv2.dilate(horizontal, h_struct)
    vertical = cv2.erode(vertical, v_struct)
    vertical = cv2.dilate(vertical, v_struct)
    grid_mask = cv2.add(horizontal, vertical)
    cnts, _ = cv2.findContours(grid_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    cells = []
    for cnt in cnts:
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h >= min_cell_area:
            cells.append((x, y, w, h))

    # 🔧 Filter out overly large boxes based on area
    areas = [w * h for (_, _, w, h) in cells]
    if areas:
        median_area = np.median(areas)
        max_allowed_area = 2 * median_area
        cells = [(x, y, w, h) for (x, y, w, h) in cells if w * h <= max_allowed_area]

    cells.sort(key=lambda b: (b[1], b[0]))
    return cells

def image_to_searchable_pdf(image_path, pdf_path):
    orig, prep = preprocess_image(image_path)
    h_img, w_img = orig.shape[:2]

    # 1) OCR full image for paragraphs
    data = pytesseract.image_to_data(
        Image.fromarray(prep), output_type=pytesseract.Output.DICT,
        config=r'--oem 3 --psm 12 -l eng'
    )

    # 2) Detect table cells
    cells = detect_cells(prep, min_cell_area=200, grid_divisor=60)

    # 3) OCR each cell region with psm 12 at word level
    cell_text = []
    for (cx, cy, cw, ch) in cells:
        cell_img = prep[cy:cy+ch, cx:cx+cw]
        cell_data = pytesseract.image_to_data(
            Image.fromarray(cell_img), output_type=pytesseract.Output.DICT,
            config=r'--oem 3 --psm 12 -l eng'
        )
        # collect words with good confidence, sort by left
        words = []
        for i, txt in enumerate(cell_data['text']):
            if int(cell_data['conf'][i]) > 60 and txt.strip():
                words.append((cell_data['left'][i], txt))
        words.sort(key=lambda w: w[0])
        line = ' '.join(w for _, w in words)
        cell_text.append(line)

    # 4) Mark paragraph words excluding any inside cells
    used_idxs = set()
    for i in range(len(data['text'])):
        if int(data['conf'][i]) < 60 or not data['text'][i].strip():
            continue
        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
        cx, cy = x + w//2, y + h//2
        for (bx, by, bw, bh) in cells:
            if bx < cx < bx + bw and by < cy < by + bh:
                used_idxs.add(i)
                break

    # 5) Group remaining words into paragraph lines
    lines = {}
    for i in range(len(data['text'])):
        if i in used_idxs or int(data['conf'][i]) <= 60:
            continue
        txt = data['text'][i].strip()
        if not txt:
            continue
        key = (data['block_num'][i], data['par_num'][i], data['line_num'][i])
        lines.setdefault(key, []).append(i)

    # 6) Render PDF
    tmp = 'temp_page.jpg'
    Image.fromarray(cv2.cvtColor(orig, cv2.COLOR_BGR2RGB)).save(tmp)
    c = canvas.Canvas(pdf_path, pagesize=(w_img, h_img))
    c.drawImage(tmp, 0, 0, width=w_img, height=h_img)

    # 7) Draw paragraphs
    c.setFont('Helvetica', 20)
    c.setFillColorRGB(1, 1, 1, alpha=1)
    for idxs in lines.values():
        xs = [data['left'][i] for i in idxs]
        tops = [data['top'][i] for i in idxs]
        heights = [data['height'][i] for i in idxs]
        text_line = ' '.join(data['text'][i] for i in idxs)
        x = min(xs)
        avg_top = int(np.mean(tops))
        avg_h = int(np.mean(heights))
        y = h_img - avg_top - int(avg_h * 0.8)
        c.drawString(x, y, text_line)

    # 8) Draw cells and their text per cell box
    c.setStrokeColorRGB(1, 0, 0, alpha=1)
    c.setFont('Helvetica', 10)
    for (box, txt) in zip(cells, cell_text):
        x, y, w, h = box
        c.rect(x, h_img - y - h, w, h)
        if txt:
            c.drawString(x + 2, h_img - y - int(h * 0.2), txt)

    c.save()
    os.remove(tmp)
    print(f"✅ Searchable PDF saved to: {pdf_path}")

if __name__ == '__main__':
    today_str = datetime.date.today().strftime("%Y-%m-%d")

    input_path = 'input/cert.jpg'
    output_path = f'output/output_{today_str}.pdf'

    image_to_searchable_pdf(input_path, output_path)
