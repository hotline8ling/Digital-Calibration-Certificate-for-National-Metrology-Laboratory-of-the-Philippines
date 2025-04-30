from PIL import Image
import pytesseract
from reportlab.pdfgen import canvas
import cv2
import numpy as np
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    denoised = cv2.fastNlMeansDenoisingColored(image, None, 5, 10, 7, 21)
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    merged = cv2.merge((cl, a, b))
    enhanced = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
    return image, enhanced


def detect_cells(image,
                 min_cell_area=100,
                 grid_divisor=50):
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
    cells.sort(key=lambda b: (b[1], b[0]))
    return cells


def image_to_searchable_pdf(image_path, pdf_path):
    orig, prep = preprocess_image(image_path)
    h_img, w_img = orig.shape[:2]

    data = pytesseract.image_to_data(
        Image.fromarray(prep),
        output_type=pytesseract.Output.DICT,
        config=r'--oem 3 --psm 12 -l eng'
    )

    # Detect cells
    cells = detect_cells(prep, min_cell_area=200, grid_divisor=60)

    # Assign words: cell_text and paragraphs
    cell_text = {i: [] for i in range(len(cells))}
    para_indices = []
    for i, txt in enumerate(data['text']):
        if int(data['conf'][i]) < 60 or not txt.strip():
            continue
        x, y, w, hh = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
        cx, cy = x + w//2, y + hh//2
        assigned = False
        for idx, (cx0, cy0, cw, ch) in enumerate(cells):
            if cx0 < cx < cx0+cw and cy0 < cy < cy0+ch:
                cell_text[idx].append((x, txt))
                assigned = True
                break
        if not assigned:
            para_indices.append(i)

    # Group paragraphs by line
    lines = {}
    for i in para_indices:
        key = (data['block_num'][i], data['par_num'][i], data['line_num'][i])
        lines.setdefault(key, []).append(i)

    # Render PDF
    tmp = 'temp_page.jpg'
    Image.fromarray(cv2.cvtColor(orig, cv2.COLOR_BGR2RGB)).save(tmp)
    c = canvas.Canvas(pdf_path, pagesize=(w_img, h_img))
    c.drawImage(tmp, 0, 0, width=w_img, height=h_img)
    c.setFillColorRGB(1,1,1,alpha=1)
    c.setFont('Helvetica', 20)

    # Draw paragraphs
    for idxs in lines.values():
        xs = [data['left'][i] for i in idxs]
        tops = [data['top'][i] for i in idxs]
        heights = [data['height'][i] for i in idxs]
        text = ' '.join(data['text'][i] for i in idxs)
        x = min(xs)
        avg_top = int(np.mean(tops))
        avg_h = int(np.mean(heights))
        y = h_img - avg_top - int(avg_h*0.8)
        c.drawString(x, y, text)

    # Draw cells: one line per cell using cell_text
    c.setStrokeColorRGB(1,0,0)
    c.setFont('Helvetica', 12)
    for idx, (x, y, w, h) in enumerate(cells):
        c.rect(x, h_img - y - h, w, h)
        words = [txt for x0, txt in sorted(cell_text[idx], key=lambda p: p[0])]
        if words:
            line = ' '.join(words)
            tx = x + 2
            ty = h_img - y - int(h*0.2)
            c.drawString(tx, ty, line)

    c.save()
    os.remove(tmp)
    print(f"✅ Searchable PDF saved to: {pdf_path}")

if __name__ == '__main__':
    image_to_searchable_pdf('input/cert.jpg', 'output/exp/hyper/new-output.pdf')
