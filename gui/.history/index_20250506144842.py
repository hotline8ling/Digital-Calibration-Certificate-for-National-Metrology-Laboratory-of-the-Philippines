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


def open_images():
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

    # create a temp file path but don't hold it open
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp_path = tmp.name
    tmp.close()                      # release the handle so ReportLab can write

    c = canvas.Canvas(tmp_path)
    for image_path in image_files:
        print(f"🔄 Adding page: {image_path}")
        add_image_to_pdf_canvas(image_path, c)
    c.save()

    # reuse extract_pdf on our temp PDF
    cal_info = extract_pdf(tmp_path)
    if not cal_info:
        messagebox.showerror("Error", "No data extracted from the generated PDF")
        os.remove(tmp_path)
        return

    # write calibration_info to JSON and hand off to pdfToxml.py
    tmp_json = os.path.join(script_dir, "calibration_info.json")
    with open(tmp_json, "w", encoding="utf-8") as f:
        json.dump(cal_info, f, ensure_ascii=False, indent=2)

    # clean up the temporary PDF now that it's no longer needed
    os.remove(tmp_path)

    app.destroy()
    subprocess.Popen([
        sys.executable,
        os.path.join(script_dir, "imgToxml.py"),
        tmp_json
    ])



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
                        "temperature_unit": '',

                        "humidity": '',
                        "humidity_unit": '',
                        # measurement arrays – split on spaces or commas
                        "standard_measurement_values": '',
                        "standard_measurement_unit": '',
                        "measured_item_values": '',
                        "measured_item_unit": '',
                        "relative_uncertainty":"Relative Expanded Uncertainty",
                        "measured_item": "Indicated Measurement",
                        "measurement_standard": "Standard Measurement",
                        "relative_uncertainty_values": '',
                        "relative_uncertainty_unit": '',
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
            # line is all-caps (with spaces, commas, dots or hyphens), at least two words,
            # and does not start with any known header
            if (re.match(r'^[A-Z][A-Z\s,\.\-]+$', txt)
                and len(txt.split()) > 1
                and not any(txt.startswith(pref) for pref in exclude_prefixes)):
                person_indices.append(i)

        # take up to three name/role pairs
        for idx, li in enumerate(person_indices[:3]):
            info[f'resp_person{idx+1}_name'] = lines[li].strip()
            # the role should be the next non-empty line after the name
            for j in range(li+1, min(li+5, len(lines))):
                role_txt = lines[j].strip()
                if role_txt and role_txt != lines[li].strip():
                    info[f'resp_person{idx+1}_role'] = role_txt
                    break

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
        # Extract the first key of table 1 as standard measurement
        standard_measurement = list(table_columns[0].keys())[0]

        # split the uncertainty column into unit and values
        raw_standard = table_columns[0][standard_measurement]
        standard_unit = raw_standard[0]
        raw_standard_str = raw_standard[1]
        standard_val = raw_standard_str.replace('\n', ' ')

        # Extract the equipment measured values from table 1
        measured_col = next((col for col in table_columns[0]
                            if 'indicated' in col.lower()), None)
        if measured_col:
            raw_measured = table_columns[0][measured_col]
            measured_unit = raw_measured[0]
            measured_val = raw_measured[1].replace('\n', ' ')
        else:
            measured_unit = ''
            measured_val = ''

        # find uncertainty column
        uncertainty_col = next((col for col in table_columns[0]
                                if 'uncertainty' in col.lower()), "")
        if not uncertainty_col:
            raise KeyError("No uncertainty column found in table_columns[0]")

        raw_uncertainty = table_columns[0][uncertainty_col]
        uncertainty_unit = raw_uncertainty[0]
        uncertainty_str = raw_uncertainty[1]
        value_count = uncertainty_str.count('\n') + 1
        uncertainty_val = uncertainty_str.replace('\n', ' ')

        # store into calibration_info
        calibration_info.update({
            'standard_item':          instrument_name,
            'standard_serial_number': instrument_serial,
            'standard_model':         make_model,
            'standard_cert_number':   cert_number,
            'standard_traceability':  traceability,
            'relative_uncertainty':       uncertainty_col.replace('\n', ' '),
            'relative_uncertainty_unit':  ' '.join([f'\\{uncertainty_unit}'] * value_count),
            'relative_uncertainty_values': uncertainty_val,
            'measurement_standard':        standard_measurement.replace('\n', ' '),
            'standard_measurement_unit':   ' '.join([f'\\{standard_unit}'] * value_count),
            'standard_measurement_values': standard_val,
            'measured_item':               measured_col.replace('\n', ' ') if measured_col else '',
            'measured_item_unit':          ' '.join([f'\\{measured_unit}'] * value_count),
            'measured_item_values':        measured_val
        })

    except (IndexError, KeyError) as e:
        print(f"Table parsing error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    # return the calibration_info dictionary
    print(calibration_info)
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
bg_frame.place(relx=0, rely=0.242, relwidth=1, relheight=0.202)

# BG rectangle 2
bg_frame2 = CTkFrame(master=app, fg_color="#E0E0E0", corner_radius=0)
bg_frame2.place(relx=0, rely=0.458, relwidth=1, relheight=0.202)

# BG rectangle 3
bg_frame3 = CTkFrame(master=app, fg_color="#E0E0E0", corner_radius=0)
bg_frame3.place(relx=0, rely=0.674, relwidth=1, relheight=0.202)

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
certLabel.place(relx=0.124, rely=0.375)

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
importFormatL.place(relx=0.124, rely=0.478)

# import button for pdf
importFormat = CTkButton(master=app, text="Import PDF", corner_radius=7,
                    fg_color="#0855B1", hover_color="#010E54", font=("Inter", 13),command=open_pdf)
importFormat.place(relx=0.124, rely=0.524, relwidth=0.368, relheight=0.066)

# Textlabel for Calibration Format XML
formatLabel = CTkLabel(master=app, text="exampleFormat.xml", font=("Inter", 12), bg_color="#E0E0E0")
formatLabel.place(relx=0.124, rely=0.591)

# Textlabel for DCC Scratch
importFormatL = CTkLabel(master=app, text="Create a New Calibration Certificate", font=("Inter", 13), bg_color="#E0E0E0")
importFormatL.place(relx=0.124, rely=0.700)

# button for dcc-scratch
importCert = CTkButton(master=app, text="Make a new DCC File", corner_radius=7, 
                    fg_color="#0855B1", hover_color="#010E54", font=("Inter", 13),command=open_newxml_gui)
importCert.place(relx=0.124, rely=0.754, relwidth=0.368, relheight=0.066)





app.mainloop()