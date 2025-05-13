from tkinter import messagebox
from customtkinter import *
from PIL import Image
import os
import subprocess
from datetime import datetime
import cv2
from lxml import etree as LET
import json
import re
import cv2
import numpy as np
import pytesseract
from reportlab.pdfgen import canvas
import tkinter as tk
from tkinter import filedialog
import pdfplumber
import tempfile
import threading
import sys
from lxml import etree
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from PyPDF2 import PdfReader, PdfWriter



pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#import static_info.json
# Load the JSON data from the file using absolute path

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'static_info.json')
try:
    with open(config_path, 'r') as file:
        cfg = json.load(file)
except FileNotFoundError:
    print(f"Error: Could not find the configuration file at: {config_path}")
    print("Current working directory:", os.getcwd())
    print("Looking for file in directory:", script_dir)
    raise

# Center the application on the screen
def center_window(app, width, height):
    app.update_idletasks()
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    app.geometry(f"{width}x{height}+{x}+{y}")

app = CTk()
app.title("DigiCert")
app_width = 500
app_height = 500
center_window(app, app_width, app_height)  # Call the function to center the window
set_appearance_mode("light")

# Disable maximize button
app.resizable(False, False)

# Create a CTkFrame to act as the background (canvas)
bg_frame = CTkFrame(master=app, fg_color="white")  # Set the color to white
bg_frame.place(relx=0, rely=0, relwidth=1, relheight=1)  # Fill the entire window

# Functions


def show_loading_screen(text="Loading, please wait..."):
    # create a modal “loading” window
    loading = CTkToplevel(app)
    loading.geometry("300x80")
    loading.title("")
    loading.transient(app)
    loading.grab_set()  # block interaction with main window
    loading.resizable(False, False)
    lbl = CTkLabel(loading, text=text, font=("Inter", 14))
    lbl.pack(expand=True, fill="both", padx=20, pady=20)
    return loading, lbl

def export_xml_to_pdf():
    # Ask the user to pick an XML file
    xml_path = filedialog.askopenfilename(
        title="Select XML certificate",
        filetypes=[("XML files", "*.xml")]
    )
    if not xml_path:
        return

    # Suggest a PDF filename matching the XML
    default_name = os.path.splitext(os.path.basename(xml_path))[0] + ".pdf"
    # Let user choose where to save the PDF
    pdf_path = filedialog.asksaveasfilename(
        title="Save PDF As",
        defaultextension=".pdf",
        initialfile=default_name,
        initialdir=os.path.dirname(xml_path),
        filetypes=[("PDF files", "*.pdf")]
    )
    if not pdf_path:
        return

    try:
        build_pdf(xml_path, pdf_path)
        messagebox.showinfo("Success", f"PDF exported to:\n{pdf_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export PDF:\n{e}")

def text(el, default=''):
    return el.text.strip() if el is not None and el.text else default

def build_pdf(xml_path, pdf_path):
    tree = etree.parse(xml_path)
    root = tree.getroot()
    NS = root.nsmap or {}                       # automatically map XML namespaces
    styles = getSampleStyleSheet()
    story = []

    # SOFTWARE USED
    story.append(Paragraph("SOFTWARE USED", styles['Heading2']))
    sw_name = root.find(".//dcc:dccSoftware//dcc:content", namespaces=NS)
    sw_ver  = root.find(".//dcc:dccSoftware//dcc:release",   namespaces=NS)
    story.append(Paragraph(f"Software Name: {text(sw_name)}", styles['Normal']))
    story.append(Paragraph(f"Software Version: {text(sw_ver)}", styles['Normal']))
    story.append(Spacer(1,12))

    # ADMINISTRATIVE DATA – CORE DATA
    story.append(Paragraph("ADMINISTRATIVE DATA", styles['Heading2']))
    core = root.find(".//dcc:coreData", namespaces=NS)
    uid = core.find("dcc:uniqueIdentifier", namespaces=NS)
    bpd = core.find("dcc:beginPerformanceDate", namespaces=NS)
    epd = core.find("dcc:endPerformanceDate",   namespaces=NS)
    loc = core.find("dcc:performanceLocation",  namespaces=NS)
    story.append(Paragraph("CORE DATA", styles['Heading3']))
    story.append(Paragraph(f"Unique Identifier: {text(uid)}", styles['Normal']))
    story.append(Paragraph(f"Start Performance Date: {text(bpd)}", styles['Normal']))
    story.append(Paragraph(f"End Performance Date: {text(epd)}", styles['Normal']))
    story.append(Paragraph(f"Performance Location: {text(loc)}", styles['Normal']))
    story.append(Spacer(1,12))

    # EQUIPMENTS USED
    items = root.findall(".//dcc:item", namespaces=NS)
    # assume first is calibration, second is standard
    cal, std = items
    story.append(Paragraph("EQUIPMENTS USED", styles['Heading2']))

    # STANDARD EQUIPMENT
    story.append(Paragraph("STANDARD EQUIPMENT", styles['Heading3']))
    std_name  = std.find("dcc:name//dcc:content", namespaces=NS)
    std_model = std.find("dcc:model", namespaces=NS)
    std_id    = std.find("dcc:identifications//dcc:identification", namespaces=NS)
    std_sn    = std_id.find("dcc:name//dcc:content", namespaces=NS)
    std_cert  = std.find("dcc:description//dcc:content[1]", namespaces=NS)
    std_trace = std.find("dcc:description//dcc:content[2]", namespaces=NS)
    story.append(Paragraph(f"Standard Equipment Name: {text(std_name)}", styles['Normal']))
    story.append(Paragraph(f"Standard Equipment Model: {text(std_model)}", styles['Normal']))
    story.append(Paragraph(f"Standard Equipment Serial Number: {text(std_sn)}", styles['Normal']))
    story.append(Paragraph(f"Standard Equipment Cert No.: {text(std_cert)}", styles['Normal']))
    story.append(Paragraph(f"Standard Equipment {text(std_trace)}", styles['Normal'])) # Traceability
    story.append(Spacer(1,12))

    # CALIBRATION EQUIPMENT
    story.append(Paragraph("CALIBRATION EQUIPMENT", styles['Heading3']))
    cal_name   = cal.find("dcc:name//dcc:content", namespaces=NS)
    cal_model  = cal.find("dcc:model", namespaces=NS)
    cal_id     = cal.find("dcc:identifications//dcc:identification", namespaces=NS)
    cal_sn     = cal_id.find("dcc:name//dcc:content", namespaces=NS)
    descs      = cal.findall("dcc:description//dcc:content", namespaces=NS)
    story.append(Paragraph(f"Calibration Equipment Name: {text(cal_name)}", styles['Normal']))
    story.append(Paragraph(f"Calibration Equipment Model: {text(cal_model)}", styles['Normal']))
    story.append(Paragraph(f"Calibration Equipment Serial Number: {text(cal_sn)}", styles['Normal']))
    # description lines
    story.append(Paragraph(f"Calibration Equipment {text(descs[0])}", styles['Normal'])) # Capacity
    story.append(Paragraph(f"Calibration Equipment {text(descs[1])}", styles['Normal'])) # Range
    story.append(Paragraph(f"Calibration Equipment {text(descs[2])}", styles['Normal'])) #Resolution
    story.append(Spacer(1,12))

    # CALIBRATION LABORATORY
    lab = root.find(".//dcc:calibrationLaboratory", namespaces=NS)
    code = lab.find("dcc:calibrationLaboratoryCode", namespaces=NS)
    lab_name = lab.find("dcc:contact//dcc:content", namespaces=NS)
    city = lab.find("dcc:contact//dcc:city", namespaces=NS)
    country = lab.find("dcc:contact//dcc:countryCode", namespaces=NS)
    post = lab.find("dcc:contact//dcc:postCode", namespaces=NS)
    street = lab.find("dcc:contact//dcc:street", namespaces=NS)
    story.append(Paragraph("CALIBRATION LABORATORY", styles['Heading2']))
    story.append(Paragraph(f"Laboratory Code: {text(code)}", styles['Normal']))
    story.append(Paragraph(f"Laboratory Name: {text(lab_name)}", styles['Normal']))
    addr = f"{text(street)}, {text(city)}, {text(country)}, {text(post)}"
    story.append(Paragraph(f"Laboratory Address: {addr}", styles['Normal']))
    story.append(Spacer(1,12))

    # RESPONSIBLE PERSON/S
    story.append(Paragraph("RESPONSIBLE PERSON/S", styles['Heading2']))
    for i, rp in enumerate(root.findall(".//dcc:respPerson", namespaces=NS), 1):
        name = rp.find("dcc:person//dcc:content", namespaces=NS)
        role = rp.find("dcc:role", namespaces=NS)
        story.append(Paragraph(f"PERSON {i} NAME: {text(name)}", styles['Normal']))
        story.append(Paragraph(f"PERSON {i} ROLE: {text(role)}", styles['Normal']))
    story.append(Spacer(1,12))

    # CUSTOMER INFORMATION
    cust = root.find(".//dcc:customer", namespaces=NS)
    cname = cust.find("dcc:name//dcc:content", namespaces=NS)
    cloc  = cust.find("dcc:location//dcc:content", namespaces=NS)
    story.append(Paragraph("CUSTOMER INFORMATION", styles['Heading2']))
    story.append(Paragraph(f"Customer Name: {text(cname)}", styles['Normal']))
    story.append(Paragraph(f"Customer Location: {text(cloc)}", styles['Normal']))
    story.append(Spacer(1,12))

    # MEASUREMENT RESULTS
    story.append(Paragraph("MEASUREMENT RESULTS", styles['Heading2']))
    meas = root.find(".//dcc:measurementResults", namespaces=NS)
    mname = meas.find("dcc:name//dcc:content", namespaces=NS)
    story.append(Paragraph(f"Calibration Equipment Name: {text(mname)}", styles['Normal']))
    # used method
    um = meas.find(".//dcc:usedMethod", namespaces=NS)
    unc_desc = um.find("dcc:description//dcc:content", namespaces=NS)
    story.append(Paragraph("Used Methods", styles['Heading3']))
    story.append(Paragraph(f"Uncertainty: {text(unc_desc)}", styles['Normal']))
    story.append(Spacer(1,12))
    # influence conditions
    story.append(Paragraph("InfluenceConditions", styles['Heading3']))
    for ref in [("basic_temperature","Temperature"),("basic_humidityRelative","Humidity")]:
        ic = meas.find(f".//dcc:influenceCondition[@refType='{ref[0]}']", namespaces=NS)
        val = ic.find("dcc:data//si:value", namespaces=NS)
        unit= ic.find("dcc:data//si:unit", namespaces=NS)
        story.append(Paragraph(f"{ref[1]}: {text(val)} {text(unit)}", styles['Normal']))
    story.append(Spacer(1,12))


   # Results table
    story.append(Paragraph("Results", styles['Heading3']))
    results = meas.findall(".//dcc:result", namespaces=NS)

    # define a header paragraph style to allow word wrapping and centering
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], alignment=1)
    # 1) Column headers from <dcc:name>, wrapped as Paragraphs to avoid overlap
    headers = [
        Paragraph(text(r.find("dcc:name//dcc:content", namespaces=NS), 'null'), header_style)
        for r in results
    ]

    # 2) Extract raw tokens, merge them, and collect units
    data_cols = []
    unit_cols = []
    for r in results:
        v_el = r.find(".//si:valueXMLList", namespaces=NS)
        u_el = r.find(".//si:unitXMLList",   namespaces=NS)

        raw_vals = v_el.text.split() if v_el is not None and v_el.text else []
        vals = raw_vals if raw_vals else ['null']

        units = u_el.text.split() if u_el is not None and u_el.text else ['']
        data_cols.append(vals)
        unit_cols.append(units)

    # 3) Build the unit row (take first unit of each column)
    unit_row = [
        u_list[0] if u_list and u_list[0] else ''
        for u_list in unit_cols
    ]

    # 4) Build value rows
    max_rows = max((len(col) for col in data_cols), default=0)
    table_data = [headers, unit_row]
    for i in range(max_rows):
        row = [
            data_cols[j][i] if i < len(data_cols[j]) else 'null'
            for j in range(len(data_cols))
        ]
        table_data.append(row)

    # 5) Create table (repeat both header rows if it spills pages) 
    # everything is centered
    tbl = Table(
        table_data,
        colWidths=[(LETTER[0] - 144) / len(headers)] * len(headers),
        repeatRows=2,
        hAlign='CENTER',               # center the table on the page
        rowHeights=[None] * len(table_data),
    )
    tbl.setStyle(TableStyle([
       # center all cells
       ('ALIGN',         (0, 0),   (-1, -1),  'CENTER'),

       # header row
       ('BACKGROUND',    (0,0),   (-1,0),   colors.HexColor('#4F81BD')),
       ('TEXTCOLOR',     (0,0),   (-1,0),   colors.white),
       ('FONTNAME',      (0,0),   (-1,0),   'Helvetica-Bold'),
       ('FONTSIZE',      (0,0),   (-1,0),   11),
       ('BOTTOMPADDING', (0,0),   (-1,0),   8),

       # unit row
       ('BACKGROUND',    (0,1),   (-1,1),   colors.HexColor('#DCE6F1')),
       ('FONTNAME',      (0,1),   (-1,1),   'Helvetica-Oblique'),

       # alternating row backgrounds
       ('ROWBACKGROUNDS',(0,2),   (-1,-1),  [colors.white, colors.HexColor('#F2F2F2')]),
       ('GRID',          (0,0),   (-1,-1),  0.5, colors.grey),

       # padding for all cells
       ('LEFTPADDING',   (0,0),   (-1,-1),  6),
       ('RIGHTPADDING',  (0,0),   (-1,-1),  6),
       ('TOPPADDING',    (0,0),   (-1,-1),  4),
       ('BOTTOMPADDING', (0,0),   (-1,-1),  4),
    ]))
    story.append(tbl)
    story.append(Spacer(1,12))

    # COMMENT
    story.append(Paragraph("COMMENT", styles['Heading2']))
    cmts = root.findall(".//dcc:comment//dcc:content", namespaces=NS)
    story.append(Paragraph(f"{text(cmts[0])}", styles['Normal'])) # Calibration Procedure
    story.append(Spacer(1,12))
    story.append(Paragraph(f"{text(cmts[1])}", styles['Normal'])) # Remarks

    doc = SimpleDocTemplate(pdf_path, pagesize=LETTER)
    doc.build(story)


# You can then hook this up to a button:
exportXML_button = CTkButton(
    master=app,
    text="Convert XML → PDF",
    corner_radius=7,
    fg_color="#0855B1",
    hover_color="#010E54",
    font=("Inter", 13),
    command=export_xml_to_pdf
)
exportXML_button.place(relx=0.124, rely=0.842, relwidth=0.368, relheight=0.066)


def open_images():
    #Display a messagebox to inform the user that image to xml is not the most reliant option since it there are many factors that can affect the result such as lighting, image quality, etc.
    messagebox.showinfo("Info", "Image to XML is not the most reliable option. Please check the results carefully.")


    # Hide root and open multi-file dialog
    root = tk.Tk()
    root.withdraw()
    image_files = filedialog.askopenfilenames(
        title="Select image files",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
    )
    if not image_files:
        print("❌ No images selected.")
        return

    # 2) show “loading” overlay
    loading_win, loading_label = show_loading_screen("Processing images...")

    def worker():
        # build temp PDF
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        tmp_path = tmp.name;  tmp.close()
        c = canvas.Canvas(tmp_path)
        for i, image_path in enumerate(image_files, 1):
            # optional: update loading text
            app.after(0, lambda i=i: loading_label.configure(
                text=f"Processing image {i}/{len(image_files)}..."
            ))
            add_image_to_pdf_canvas(image_path, c)
        c.save()

        # extract & hand off
        cal_info = extract_pdf(tmp_path)
        os.remove(tmp_path)
        if not cal_info:
            app.after(0, lambda:
                messagebox.showerror("Error", "No data extracted")
            )
            return

        tmp_json = os.path.join(script_dir, "calibration_info.json")
        print("Writing to:", tmp_json)
        with open(tmp_json, "w", encoding="utf-8") as f:
            json.dump(cal_info, f, ensure_ascii=False, indent=2)

        # close loading, then main window, then launch xml GUI
        def finish():
            loading_win.destroy()
            app.destroy()
            subprocess.Popen([
                sys.executable,
                os.path.join(script_dir, "imgToxml.py"),
                tmp_json
            ])
        app.after(0, finish)

    # run the work in background so UI stays responsive
    threading.Thread(target=worker, daemon=True).start()



def preprocess_image(image_path):
    image = cv2.imread(image_path)
    denoised = cv2.fastNlMeansDenoisingColored(image, None, 5, 10, 7, 21)
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    blur = cv2.GaussianBlur(cl, (5, 5), sigmaX=1.0)
    sharp_l = cv2.addWeighted(cl, 1.3, blur, -0.3, 0)
    merged = cv2.merge((sharp_l, a, b))
    enhanced = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
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
    areas = [w * h for (_, _, w, h) in cells]
    if areas:
        median_area = np.median(areas)
        max_allowed_area = 2 * median_area
        cells = [(x, y, w, h) for (x, y, w, h) in cells if w * h <= max_allowed_area]
    cells.sort(key=lambda b: (b[1], b[0]))
    return cells

def add_image_to_pdf_canvas(image_path, c):
    orig, prep = preprocess_image(image_path)
    h_img, w_img = orig.shape[:2]

    data = pytesseract.image_to_data(
        Image.fromarray(prep), output_type=pytesseract.Output.DICT,
        config=r'--oem 3 --psm 12 -l eng'
    )

    cells = detect_cells(prep, min_cell_area=200, grid_divisor=60)
    cell_text = []
    for (cx, cy, cw, ch) in cells:
        cell_img = prep[cy:cy+ch, cx:cx+cw]
        cell_data = pytesseract.image_to_data(
            Image.fromarray(cell_img), output_type=pytesseract.Output.DICT,
            config=r'--oem 3 --psm 12 -l eng'
        )
        words = []
        for i, txt in enumerate(cell_data['text']):
            if int(cell_data['conf'][i]) > 60 and txt.strip():
                words.append((cell_data['left'][i], txt))
        words.sort(key=lambda w: w[0])
        line = ' '.join(w for _, w in words)
        cell_text.append(line)

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

    lines = {}
    for i in range(len(data['text'])):
        if i in used_idxs or int(data['conf'][i]) <= 60:
            continue
        txt = data['text'][i].strip()
        if not txt:
            continue
        key = (data['block_num'][i], data['par_num'][i], data['line_num'][i])
        lines.setdefault(key, []).append(i)

        tmp = f'temp_page_{os.path.basename(image_path)}.jpg'
        Image.fromarray(cv2.cvtColor(orig, cv2.COLOR_BGR2RGB)).save(tmp)
        c.setPageSize((w_img, h_img))
        c.drawImage(tmp, 0, 0, width=w_img, height=h_img)


    c.setFont('Helvetica', 20)
    c.setFillColorRGB(1, 1, 1, alpha=0)
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

    c.setStrokeColorRGB(1, 0, 0, alpha=0)
    c.setFont('Helvetica', 10)
    for (box, txt) in zip(cells, cell_text):
        x, y, w, h = box
        c.rect(x, h_img - y - h, w, h)
        if txt:
            c.drawString(x + 2, h_img - y - int(h * 0.2), txt)

    os.remove(tmp)
    c.showPage()

def open_pdf():
    pdf_path = filedialog.askopenfilename(filetypes=[("PDF files","*.pdf")])
    if not pdf_path:
        return
    cal_info = extract_pdf(pdf_path)
    if not cal_info:
        messagebox.showerror("Error","No data extracted")
        return

    # write to a well-known temp JSON
    tmp = os.path.join(script_dir, "calibration_info.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cal_info, f, ensure_ascii=False, indent=2)

    app.destroy()
    # pass the JSON file, not the PDF!
    subprocess.Popen([sys.executable,
                      os.path.join(script_dir, "pdfToxml.py"),
                      tmp])

def open_newxml_gui():
    app.destroy()  # Close the current app window
    subprocess.Popen(["python",  os.path.join(os.path.dirname(__file__),"new-xml.py")])

def open_settings():
    app.destroy()  # Close the current app window
    subprocess.Popen(["python",  os.path.join(os.path.dirname(__file__),"settings.py")])  # Open the settings.py file

def extract_pdf(pdf_path):
    def extract_text(path):
        with pdfplumber.open(path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
        
    raw_text = extract_text(pdf_path)
        
    def extract_table_columns(path):
            tables_columns = []
            # tune these strategies if your PDF’s ruling lines or text‐based layout differs
            table_settings = {
                "vertical_strategy":   "lines",
                "horizontal_strategy": "lines",
                "intersection_tolerance": 5
            }

            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    # pass the settings here
                    tables = page.extract_tables(table_settings)
                    for table in tables:
                        if not table or len(table) < 2:
                            continue

                        # find the first row with >50% non‐empty cells → assume header
                        header_idx = next(
                            (i for i, row in enumerate(table)
                            if sum(bool(cell and cell.strip()) for cell in row) >= len(row) // 2),
                            0
                        )
                        headers = [cell.strip() for cell in table[header_idx] if cell]

                        # init dict
                        columns_data = {h: [] for h in headers if h}

                        # iterate data rows
                        for row in table[header_idx + 1:]:
                            for h, cell in zip(headers, row):
                                if h and cell and cell.strip():
                                    columns_data[h].append(cell.strip())

                        if any(columns_data.values()):
                            tables_columns.append(columns_data)

            return tables_columns

        # usage remains the same
    table_columns = extract_table_columns(pdf_path)

    # Use script_dir instead of hard-coded path
    config_path = os.path.join(script_dir, 'static_info.json')
    try:
        with open(config_path, 'r') as file:
            cfg = json.load(file)
    except FileNotFoundError:
        print(f"Error: Could not find the configuration file at: {config_path}")
        print("Current working directory:", os.getcwd())
        print("Looking for file in directory:", script_dir)
        raise


    def extract_calibration_info(raw_text):
           # Initialize variables to store extracted information
        info = {
                        "software_name": cfg["software_name"],
                        "software_release": cfg["software_release"],
                        "country_code_iso": cfg["country_code_iso"],
                        "used_lang_code": cfg["used_lang_code"],
                        "mandatory_lang_code": cfg["mandatory_lang_code"],
                        "calibration_labcode": cfg["calibration_lab"]["code"],
                        "calibration_contactname": cfg["calibration_lab"]["contact"],
                        "calibration_labcity": cfg["calibration_lab"]["city"],
                        "calibration_labcountrycode": cfg["calibration_lab"]["countrycode"],
                        "calibration_lab_postcode": cfg["calibration_lab"]["postcode"],
                        "calibration_labstreet": cfg["calibration_lab"]["street"],

                        'certificate_number': '',
                        'calibration_date': '',
                        'calibration_enddate': '',
                        'calibration_location': 'Laboratory',

                        # Items
                        'calibration_item': '',
                        "make_model": '',
                        "serial_number": '',
                        "capacity": '',
                        "measurement_range": '',
                        "resolution": '',
                        "identification_issuer": 'Not given',

                        # Standard equipment
                        "standard_item": '',            
                        "standard_model": '',           
                        "standard_serial_number": '',           
                        "standard_cert_number": '',              
                        "standard_traceability": '',
                        "standard_item_issuer": 'Not given',  

                        # Persons
                        "resp_person1_name": '',
                        "resp_person1_role": '',
                        "resp_person2_name": '',
                        "resp_person2_role": '',
                        "resp_person3_name": '',
                        "resp_person3_role": '',

                        # Customer
                        "customer_name": '',
                        "customer_address": '',
                        # Environment & results
                        "temperature": '',
                        "temperature_unit": '\\celcius',

                        "humidity": '',
                        "humidity_unit": '\\%',
                        # measurement arrays – split on spaces or commas
                        'standard_item':          '',
                        'standard_serial_number': '',
                        'standard_model':         '',
                        'standard_cert_number':   '',
                        'standard_traceability':  '',
                        'measurement_standard':     ''   ,
                        'standard_measurement_unit': '',
                        'standard_measurement_values': '',
                        'measured_item':      '',
                        'measured_item_unit':  '',
                        'measured_item_values': ''       ,
                        'measurement_error':     ''    ,
                        'measurement_error_unit': ''   ,
                        'measurement_error_values': '' ,
                        'relative_uncertainty':     '' ,
                        'relative_uncertainty_unit': '' ,
                        'relative_uncertainty_values':'',
                        'repeatability_error':      '',
                        'repeatability_error_unit':  '',
                        'repeatability_error_values': '',

                        # big text‐areas
                        "calibration_procedure": '',
                        "remarks": '',
                        "uncertainty_of_measurement": '',

         }     
        # Split text into lines for easier processing
        lines = raw_text.split('\n')
        
            # Extract certificate number using regex
        cert_match = re.search(r'No\.\s+([\w\-]+)', raw_text)
        if cert_match:
            info['certificate_number'] = cert_match.group(1)
        
        # Extract calibration date using regex (with or without colon)
        date_match = re.search(r'Date of Calibration(?:\s*:\s*|\s+)([^\n]+)', raw_text)
        if date_match:
            info['calibration_date'] = date_match.group(1).strip()
        # Extract calibration item
        item_match = re.search(r'Calibration Item(?:\s*:\s*|\s+)([^\n]+)', raw_text)
        if item_match:
            info['calibration_item'] = item_match.group(1).strip()
        
        # Extract capacity
        capacity_match = re.search(r'Capacity(?:\s*:\s*|\s+)([^\n]+)', raw_text)
        if capacity_match:
            info['capacity'] = capacity_match.group(1).strip()
        
        # Extract measurement range
        range_match = re.search(r'Measurement Range(?:\s*:\s*|\s+)([^\n]+)', raw_text)
        if range_match:
            info['measurement_range'] = range_match.group(1).strip()
        
        # Extract resolution
        resolution_match = re.search(r'Resolution(?:\s*:\s*|\s+)([^\n]+)', raw_text)
        if resolution_match:
            info['resolution'] = resolution_match.group(1).strip()
        
        # Extract make/model
        make_match = re.search(r'Make / Model(?:\s*:\s*|\s+)([^\n]+)', raw_text)
        if make_match:
            info['make_model'] = make_match.group(1).strip()
        
        # Extract serial number
        serial_match = re.search(r'Serial No\.(?:\s*:\s*|\s+)([^\n]+)', raw_text)
        if serial_match:
            info['serial_number'] = serial_match.group(1).strip()
        
        # Extract customer and address
        # First find the customer line
        customer_match = re.search(r'Customer(?:\s*:\s*|\s+)([^\n]+)', raw_text)
        if customer_match:
            info['customer_name'] = customer_match.group(1).strip()
            
            # Find the address (typically the line after customer)
            customer_line_index = -1
            for i, line in enumerate(lines):
                if 'Customer :' in line or 'Customer:' in line:
                    customer_line_index = i
                    break
            
            # If we found the customer line and there's at least one more line after it
            if customer_line_index != -1 and customer_line_index + 1 < len(lines):
                # The next line is likely the address
                address_line = lines[customer_line_index + 1].strip()
                
                # Check if the next line appears to be an address (not a section header)
                if address_line and not address_line.isupper() and 'MEASUREMENT' not in address_line:
                    info['customer_address'] = address_line
                
                # If we might need to look for more address lines
                next_section_idx = -1
                for i in range(customer_line_index + 1, len(lines)):
                    if 'MEASUREMENT' in lines[i] or 'RESULTS' in lines[i]:
                        next_section_idx = i
                        break
                
                # If we found a section header and there might be more address lines
                if next_section_idx != -1 and customer_line_index + 1 < next_section_idx - 1:
                    # Collect all lines between customer and next section
                    address_lines = []
                    for i in range(customer_line_index + 1, next_section_idx):
                        if lines[i].strip():  # If not empty
                            address_lines.append(lines[i].strip())
                    
                    if address_lines:
                        info['customer_address'] = ' '.join(address_lines)
                        
                # Extract environmental conditions (with or without colon)
        temp_match = re.search(
            r'Ambient Temperature(?:\s*:\s*|\s+)\(?([^\)\n]+)\)?',
            raw_text
        )
        if temp_match:
            info['temperature'] = temp_match.group(1).strip()

        hum_match = re.search(
            r'Relative Humidity(?:\s*:\s*|\s+)\(?([^\)\n]+)\)?',
            raw_text
        )
        if hum_match:
            info['humidity'] = hum_match.group(1).strip()
        # --- Replace old respPerson logic with this new block ---
        # Extract responsible persons by finding uppercase name lines and their following role lines
        exclude_prefixes = (
            'CALIBRATION', 'UNCERTAINTY', 'STANDARD', 'ENVIRONMENTAL',
            'PAGE', 'MEASUREMENT', 'REMARKS', 'DATE', '-END'
        )
        person_indices = []
        for i, line in enumerate(lines):
            txt = line.strip()
            if (re.match(r'^[A-Z][A-Z\s,\.\-]+$', txt)
                and len(txt.split()) > 1
                and not any(txt.startswith(pref) for pref in exclude_prefixes)):
                person_indices.append(i)

        # take up to two name/role pairs for persons 1 and 2
        for idx, li in enumerate(person_indices[:2]):
            info[f'resp_person{idx+1}_name'] = lines[li].strip()
            for j in range(li+1, min(li+5, len(lines))):
                role_txt = lines[j].strip()
                if role_txt and role_txt != lines[li].strip():
                    info[f'resp_person{idx+1}_role'] = role_txt
                    break

        # Extract 3rd person (Chief) between "For the Chief, National Metrology Laboratory" and "Date issued:"
        chief_match = re.search(
            r'For the Chief, National Metrology Laboratory\s*(.*?)\s*Date issued:',
            raw_text,
            re.DOTALL
        )
        if chief_match:
            block_lines = [l.strip() for l in chief_match.group(1).split('\n') if l.strip()]
            if len(block_lines) >= 2:
                info['resp_person3_name'] = block_lines[0]
                info['resp_person3_role'] = block_lines[1]


        # Extract calibration procedure (with or without colon)
        proc_match = re.search(
            r'CALIBRATION PROCEDURE(?:\s*:\s*|\s+)(.*?)(?=\nENVIRONMENTAL CONDITIONS:)',
            raw_text,
            re.DOTALL
        )
        if proc_match:
            info['calibration_procedure'] = proc_match.group(1).strip()
        else:
            info['calibration_procedure'] = ''
        
        # Extract REMARKS
        remarks = []
        in_remarks = False
        current_remark = ""
        for line in lines:
            stripped = line.strip()
            # enter remarks section
            if not in_remarks:
                if stripped.startswith("REMARKS"):
                    in_remarks = True
                continue

            # stop if we hit a new all‑caps section or a line that’s fully uppercase (and not a bullet)
            if (stripped.isupper() and not stripped.startswith("-")) or re.match(r'^[A-Z\s]+:$', stripped):
                break

            # new bullet
            if stripped.startswith("-"):
                if current_remark:
                    remarks.append(current_remark.strip())
                current_remark = stripped.lstrip("- ").strip()
            # continuation of the previous bullet
            elif current_remark:
                current_remark += " " + stripped

        # append last collected remark
        if current_remark:
            remarks.append(current_remark.strip())

        # prefix each bullet with “- ” and join
        info['remarks'] = " ".join(f"- {r}" for r in remarks)

        # Extract uncertainty of measurement narrative, stopping at next section header or page break
        uom_match = re.search(
            r'UNCERTAINTY OF MEASUREMENT(?::\s*|\s+)(.*?)(?=\n[A-Z ]+?:|\nPage\s*\d+\s*of\s*\d+)',
            raw_text,
            re.DOTALL
        )
        if uom_match:
            info['uncertainty_of_measurement'] = uom_match.group(1).strip()
        else:
            info['uncertainty_of_measurement'] = ''


        

        # Clean up data …
        for key, val in info.items():
            if isinstance(val, str):
                info[key] = re.sub(r'\s+', ' ', val).strip()
        
        # Clean up data - remove any unwanted characters or fix formatting issues
        for key in info:
            # Clean up extra spaces
            if isinstance(info[key], str):
                info[key] = re.sub(r'\s+', ' ', info[key]).strip()
                # Fix specific formatting issues
                info[key] = info[key].replace(' ,', ',').replace(' .', '.')
                info[key] = info[key].replace(' ;', ';').replace(' :', ':')
        
        return info

    calibration_info = extract_calibration_info(raw_text)
    calibration_info



    def extract_table_columns(path):
            tables_columns = []
            
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    
                    for table in tables:
                        if not table or len(table) < 2:  # Skip empty tables or tables with only headers
                            continue
                        
                        # Assume first row contains headers
                        headers = table[0]
                        
                        # Create dictionary to store columns data
                        columns_data = {}
                        
                        # Initialize dictionary with header names as keys and empty lists as values
                        for header in headers:
                            if header:  # Skip empty headers
                                columns_data[header] = []
                        
                        # Fill in column data from remaining rows
                        for row in table[1:]:
                            for i, cell in enumerate(row):
                                if i < len(headers) and headers[i] and cell:
                                    columns_data[headers[i]].append(cell)
                        
                        tables_columns.append(columns_data)
            
            return tables_columns

        # Usage
    table_columns = extract_table_columns(pdf_path)
    
    # extract instrument name and serial number from Table 2
    # extract instrument name and serial number from Table 2
    try:
        # extract instrument name and serial number from Table 2
        std_entry = table_columns[1]['Name of Standard'][0]
        lines = std_entry.split('\n')
        instrument_name = ' '.join(lines[:-1]).strip()
        instrument_serial = lines[-1].strip()

        # Extract Make/Model from table 2 without newlines
        make_model = " ".join(table_columns[1]['Make/Model'][0].split())

        # Extract calibration certificate number from table 2
        cert_number = table_columns[1]['Calibration Certificate No.'][0]

        # Extract traceability from table 2
        traceability = " ".join(table_columns[1]['Traceability'][0].split())

        #------------------------------------------------ MEASUREMENT RESULTS TABLE --------------------------------------------------
        # MEASUREMENT RESULTS TABLE
        # Get the first table from table_columns which should be the measurement results
        results_table = table_columns[0]

        # Find the standard measurement column (typically "Applied Force" or similar)
        standard_col = next((col for col in results_table.keys() 
                            if any(term in col.lower() for term in ['applied', 'standard'])), 
                            list(results_table.keys())[0])  # Default to first column if not found
        standard_measurement = standard_col.replace('\n', ' ')

        # Get the unit and values from the standard column
        raw_standard = results_table[standard_col]
        standard_vals = []
        standard_unit = ''
        
        if isinstance(raw_standard, list) and raw_standard:
            # first element short? → unit
            if isinstance(raw_standard[0], str) and len(raw_standard[0]) <= 5:
                standard_unit = raw_standard[0].strip()
                cells = raw_standard[1:]
            else:
                cells = raw_standard

            # split any “\n” in each cell into separate values
            for cell in cells:
                for part in str(cell).split('\n'):
                    part = part.strip()
                    if not part:
                        continue
                    # collapse spaces inside pure-number tokens
                    if re.match(r'^[\d\s\.]+$', part):
                        part = re.sub(r'\s+', '', part)
                    standard_vals.append(part)

        elif isinstance(raw_standard, str):
            lines = [l.strip() for l in raw_standard.split('\n') if l.strip()]
            if len(lines) > 1:
                standard_unit = lines[0]
                standard_vals = lines[1:]
            else:
                standard_vals = lines

        else:
            standard_vals = [str(raw_standard)]

        standard_val = ' '.join(standard_vals)

        # Count the number of standard values for later unit repetition
        value_count = len(standard_vals)


        # Find the measured/indicated values column
        measured_col = next((col for col in results_table.keys() 
                            if any(term in col.lower() for term in ['indicated','measured','reading'])), 
                            None)
        if measured_col:
            raw_measured = results_table[measured_col]
            measured_vals = []
            measured_unit = ''

            if isinstance(raw_measured, list) and raw_measured:
                # treat first short element as unit
                if isinstance(raw_measured[0], str) and len(raw_measured[0]) <= 5:
                    measured_unit = raw_measured[0].strip()
                    cells = raw_measured[1:]
                else:
                    cells = raw_measured

                # flatten any “\n” inside each cell
                for cell in cells:
                    for part in str(cell).split('\n'):
                        part = part.strip()
                        if not part:
                            continue
                        # collapse spaces inside pure-number tokens
                        if re.match(r'^[\d\s\.]+$', part):
                            part = re.sub(r'\s+', '', part)
                        measured_vals.append(part)

            elif isinstance(raw_measured, str):
                lines = [l.strip() for l in raw_measured.split('\n') if l.strip()]
                if len(lines) > 1:
                    measured_unit = lines[0]
                    measured_vals = lines[1:]
                else:
                    measured_vals = lines

            else:
                measured_vals = [str(raw_measured)]

            measured_val = ' '.join(measured_vals)

        else:
            measured_col = ''
            measured_unit = ''
            measured_val = ''

        # Find the uncertainty column - look for "uncertainty" first
        uncertainty_col = next((col for col in results_table.keys() 
                                if 'uncertainty' in col.lower()), 
                            None)
        if not uncertainty_col:
            # Try alternative names if "uncertainty" not found
            uncertainty_col = next((col for col in results_table.keys() 
                                    ), 
                                "")
            if not uncertainty_col:
                raise KeyError("No uncertainty column found in table_columns[0]")

        raw_uncertainty = results_table[uncertainty_col]
        # Handle different possible formats
        uncertainty_vals = []
        uncertainty_unit = ''
        if isinstance(raw_uncertainty, list) and raw_uncertainty:
            # treat first short element as unit
            if isinstance(raw_uncertainty[0], str) and len(raw_uncertainty[0]) <= 5:
                uncertainty_unit = raw_uncertainty[0].strip()
                cells = raw_uncertainty[1:]
            else:
                cells = raw_uncertainty
            for cell in cells:
                for part in str(cell).split('\n'):
                    part = part.strip()
                    if not part:
                        continue
                    # collapse spaces in purely numeric tokens
                    if re.match(r'^[\d\s\.]+$', part):
                        part = re.sub(r'\s+', '', part)
                    uncertainty_vals.append(part)
        elif isinstance(raw_uncertainty, str):
            for part in raw_uncertainty.split('\n'):
                part = part.strip()
                if not part:
                    continue
                if re.match(r'^[\d\s\.]+$', part):
                    part = re.sub(r'\s+', '', part)
                uncertainty_vals.append(part)
        else:
            uncertainty_vals = [str(raw_uncertainty)]
        uncertainty_val = ' '.join(uncertainty_vals)

            
        # Find the relative measurement error or accuracy error column
        error_col = next((col for col in results_table.keys() 
                        if any(term.lower() in col.lower().replace('\n', ' ') for term in ['measurement error', 'accuracy error'])), 
                        None)
        
        if error_col:
            raw_error = results_table[error_col]
            # Handle different possible formats
            error_vals = []
            error_unit = ''
            if isinstance(raw_error, list) and raw_error:
                if isinstance(raw_error[0], str) and len(raw_error[0]) <= 5:
                    error_unit = raw_error[0].strip()
                    cells = raw_error[1:]
                else:
                    cells = raw_error
                for cell in cells:
                    for part in str(cell).split('\n'):
                        part = part.strip()
                        if not part:
                            continue
                        if re.match(r'^[\d\s\.]+$', part):
                            part = re.sub(r'\s+', '', part)
                        error_vals.append(part)
            elif isinstance(raw_error, str):
                for part in raw_error.split('\n'):
                    part = part.strip()
                    if not part:
                        continue
                    if re.match(r'^[\d\s\.]+$', part):
                        part = re.sub(r'\s+', '', part)
                    error_vals.append(part)
            else:
                error_vals = [str(raw_error)]
            error_val = ' '.join(error_vals)
                
            # Clean up column name
            error_column_name = error_col.replace('\n', ' ')
        else:
            error_column_name = "Relative Measurement Error"
            error_unit = ""
            error_val = ""



        # Find the repeatability error column
        repeatability_col = next((col for col in results_table.keys() 
                                if 'repeatability' in col.lower().replace('\n', ' ')), 
                                None)

        if repeatability_col:
            raw_repeatability = results_table[repeatability_col]
            # Handle different possible formats
            repeat_vals = []
            repeatability_unit = ''
            if isinstance(raw_repeatability, list) and raw_repeatability:
                if isinstance(raw_repeatability[0], str) and len(raw_repeatability[0]) <= 5:
                    repeatability_unit = raw_repeatability[0].strip()
                    cells = raw_repeatability[1:]
                else:
                    cells = raw_repeatability
                for cell in cells:
                    for part in str(cell).split('\n'):
                        part = part.strip()
                        if not part:
                            continue
                        if re.match(r'^[\d\s\.]+$', part):
                            part = re.sub(r'\s+', '', part)
                        repeat_vals.append(part)
            elif isinstance(raw_repeatability, str):
                for part in raw_repeatability.split('\n'):
                    part = part.strip()
                    if not part:
                        continue
                    if re.match(r'^[\d\s\.]+$', part):
                        part = re.sub(r'\s+', '', part)
                    repeat_vals.append(part)
            else:
                repeat_vals = [str(raw_repeatability)]
            repeatability_val = ' '.join(repeat_vals)
                
            # Clean up column name
            repeatability_column_name = repeatability_col.replace('\n', ' ')
        else:
            repeatability_column_name = "Relative Repeatability Error"
            repeatability_unit = ""
            repeatability_val = ""
    
        # store into calibration_info
        calibration_info.update({
            'standard_item':          instrument_name,
            'standard_serial_number': instrument_serial,
            'standard_model':         make_model,
            'standard_cert_number':   cert_number,
            'standard_traceability':  traceability,
            'measurement_standard':        standard_measurement.replace('\n', ' '),
            'standard_measurement_unit':   ' '.join([f'\\{standard_unit}'] * value_count),
            'standard_measurement_values': standard_val,
            'measured_item':               measured_col.replace('\n', ' ') if measured_col else '',
            'measured_item_unit':          ' '.join([f'\\{measured_unit}'] * value_count),
            'measured_item_values':        measured_val,
            'measurement_error':          error_column_name.replace('\n', ' '),
            'measurement_error_unit':     ' '.join([f'\\{error_unit}'] * value_count),
            'measurement_error_values':   error_val.replace('\n', ' '),
            'relative_uncertainty':       uncertainty_col.replace('\n', ' '),
            'relative_uncertainty_unit':  ' '.join([f'\\{uncertainty_unit}'] * value_count),
            'relative_uncertainty_values': uncertainty_val.replace('\n', ' '),
            'repeatability_error':       repeatability_column_name.replace('\n', ' '),
            'repeatability_error_unit':  ' '.join([f'\\{repeatability_unit}'] * value_count),
            'repeatability_error_values': repeatability_val.replace('\n', ' ')
        })
    
    except (IndexError, KeyError) as e:
        print(f"Table parsing error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    # return the calibration_info dictionary with key and value pairs
    print(calibration_info)
    calibration_info
    
    
    # Save the calibration_info to a JSON file
    # with open("calibration_info.json", "w") as f:
    #     json.dump(calibration_info, f, indent=4)
    return calibration_info


# Load and Resize the Image
image = CTkImage(light_image=Image.open(os.path.join(os.path.dirname(__file__), "itdi-logo.png")), size=(26, 25))
# Create CTkLabel with Image
image_label = CTkLabel(master=app, image=image, text="", bg_color='white') 
image_label.place(relx=0.886, rely=0.064) 

# Load and Resize the Image
image1 = CTkImage(light_image=Image.open(os.path.join(os.path.dirname(__file__),"nml-logo1.png")), size=(29, 28))
# Create CTkLabel with Image
image_label = CTkLabel(master=app, image=image1, text="", bg_color='white') 
image_label.place(relx=0.814, rely=0.064) 

stroke = CTkFrame(master=app, fg_color="#0855B1", corner_radius=0)
stroke.place(relx=0.106, rely=0.064, relwidth=0.006, relheight=0.0675)


# BG rectangle 1
bg_frame = CTkFrame(master=app, fg_color="#E0E0E0", corner_radius=0)
bg_frame.place(relx=0, rely=0.242, relwidth=1, relheight=0.16)

# BG rectangle 2
bg_frame2 = CTkFrame(master=app, fg_color="#E0E0E0", corner_radius=0)
bg_frame2.place(relx=0, rely=0.42, relwidth=1.0, relheight=0.16)

# BG rectangle 3
bg_frame3 = CTkFrame(master=app, fg_color="#E0E0E0", corner_radius=0)
bg_frame3.place(relx=0, rely=0.598, relwidth=1.0, relheight=0.16)

# BG rectangle 4
bg_frame4 = CTkFrame(master=app, fg_color="#E0E0E0", corner_radius=0)
bg_frame4.place(relx=0, rely=0.776, relwidth=1.0, relheight=0.16)

# Title label
titleLabel = CTkLabel(master=app, text="DigiCert", font=("Montserrat", 32, "bold"), bg_color='white')
titleLabel.place(relx=0.126, rely=0.054)

# Textlabel for Import Calibration Certificate image
importCertL = CTkLabel(master=app, text="Select a Calibration Certificate Image", font=("Inter", 13), bg_color="#E0E0E0")
importCertL.place(relx=0.124, rely=0.260)

# import button for image
importCert = CTkButton(master=app, text="Import Image", corner_radius=7, 
                    fg_color="#0855B1", hover_color="#010E54", font=("Inter", 13),command=open_images)
importCert.place(relx=0.124, rely=0.308, relwidth=0.368, relheight=0.066)

# Textlabel for Certificate Image
certLabel = CTkLabel(master=app, text="exampleCertificate.jpg", font=("Inter", 12), bg_color="#E0E0E0")
certLabel.place(relx=0.534, rely=0.31)

settings = CTkButton(
    master=app,
    text="Settings",
    corner_radius=7,
    fg_color="#010E54",
    hover_color="#010E54",
    font=("Inter", 8),  # Smaller font
    command=open_settings
)
settings.place(relx=0.83, rely=0.158, relwidth=0.11, relheight=0.048)

# Textlabel for Import Calibration Certificate image
importFormatL = CTkLabel(master=app, text="Select a Calibration Certificate PDF", font=("Inter", 13), bg_color="#E0E0E0")
importFormatL.place(relx=0.124, rely=0.44)

# import button for pdf
importFormat = CTkButton(master=app, text="Import PDF", corner_radius=7,
                    fg_color="#0855B1", hover_color="#010E54", font=("Inter", 13),command=open_pdf)
importFormat.place(relx=0.124, rely=0.485, relwidth=0.368, relheight=0.066)

# Textlabel for Calibration Format XML
formatLabel = CTkLabel(master=app, text="exampleCertificate.pdf", font=("Inter", 12), bg_color="#E0E0E0")
formatLabel.place(relx=0.534, rely=0.49)

# Textlabel for DCC Scratch
importFormatL = CTkLabel(master=app, text="Create a New Calibration Certificate", font=("Inter", 13), bg_color="#E0E0E0")
importFormatL.place(relx=0.124, rely=0.618)

# button for dcc-scratch
importCert = CTkButton(master=app, text="Make a new DCC File", corner_radius=7, 
                    fg_color="#0855B1", hover_color="#010E54", font=("Inter", 13),command=open_newxml_gui)
importCert.place(relx=0.124, rely=0.664, relwidth=0.368, relheight=0.066)

# Textlabel for XML to PDF
importFormatL = CTkLabel(master=app, text="Convert XML Certificate into PDF", font=("Inter", 13), bg_color="#E0E0E0")
importFormatL.place(relx=0.124, rely=0.796)

# import button for xml to pdf
importXML = CTkButton(master=app, text="Import XML", corner_radius=7,
                    fg_color="#0855B1", hover_color="#010E54", font=("Inter", 13),command=export_xml_to_pdf)
importXML.place(relx=0.124, rely=0.842, relwidth=0.368, relheight=0.066)

# Textlabel for Calibration Format XML
formatLabel = CTkLabel(master=app, text="exampleCertificate.xml", font=("Inter", 12), bg_color="#E0E0E0")
formatLabel.place(relx=0.528, rely=0.85)


app.mainloop()