from customtkinter import *
from PIL import Image
import os
import sys
import xml.dom.minidom
import pdfplumber
import re
from datetime import datetime
import xml.etree.ElementTree as ET

# Function to extract text from PDF
def extract_text(path):
    with pdfplumber.open(path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

# Function to extract table columns from PDF
def extract_table_columns(path):
    tables_columns = []
    # tune these strategies if your PDF's ruling lines or text‐based layout differs
    table_settings = {
        "vertical_strategy": "lines",
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
                headers = [cell.strip() for cell in table[header_idx]]

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

# Function to extract calibration information from PDF text
def extract_calibration_info(raw_text):
    # Initialize variables to store extracted information
    info = {
        'certificate_number': '',
        'calibration_date': '',
        'calibration_item': '',
        'capacity': '',
        'measurement_range': '',
        'resolution': '',
        'make_model': '',
        'serial_number': '',
        'customer_name': '',
        'customer_address': ''
    }
    
    # Split text into lines for easier processing
    lines = raw_text.split('\n')
    
    # Extract certificate number using regex
    cert_match = re.search(r'No\.\s+([\w\-]+)', raw_text)
    if cert_match:
        info['certificate_number'] = cert_match.group(1)
    
    # Extract calibration date using regex
    date_match = re.search(r'Date of Calibration\s*:\s*([^\n]+)', raw_text)
    if date_match:
        info['calibration_date'] = date_match.group(1).strip()
    
    # Extract calibration item
    item_match = re.search(r'Calibration Item\s*:\s*([^\n]+)', raw_text)
    if item_match:
        info['calibration_item'] = item_match.group(1).strip()
    
    # Extract capacity
    capacity_match = re.search(r'Capacity\s*:\s*([^\n]+)', raw_text)
    if capacity_match:
        info['capacity'] = capacity_match.group(1).strip()
    
    # Extract measurement range
    range_match = re.search(r'Measurement Range\s*:\s*([^\n]+)', raw_text)
    if range_match:
        info['measurement_range'] = range_match.group(1).strip()
    
    # Extract resolution
    resolution_match = re.search(r'Resolution\s*:\s*([^\n]+)', raw_text)
    if resolution_match:
        info['resolution'] = resolution_match.group(1).strip()
    
    # Extract make/model
    make_match = re.search(r'Make / Model\s*:\s*([^\n]+)', raw_text)
    if make_match:
        info['make_model'] = make_match.group(1).strip()
    
    # Extract serial number
    serial_match = re.search(r'Serial No\.\s*:\s*([^\n]+)', raw_text)
    if serial_match:
        info['serial_number'] = serial_match.group(1).strip()
    
    # Extract customer and address
    # First find the customer line
    customer_match = re.search(r'Customer\s*:\s*([^\n]+)', raw_text)
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
                    
    # Extract environmental conditions
    temp_match = re.search(r'Ambient Temperature\s*:\s*\(?([^\)\n]+)\)?', raw_text)
    if temp_match:
        info['temperature'] = temp_match.group(1).strip()
    
    hum_match = re.search(r'Relative Humidity\s*:\s*\(?([^\)\n]+)\)?', raw_text)
    if hum_match:
        info['humidity'] = hum_match.group(1).strip()
    
    # Extract responsible persons
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

    # Extract calibration procedure 
    proc_match = re.search(
        r'CALIBRATION PROCEDURE:\s*(.*?)\nENVIRONMENTAL CONDITIONS:',
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

        # stop if we hit a new all‑caps section or a line that's fully uppercase (and not a bullet)
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

    # prefix each bullet with "- " and join
    info['remarks'] = " ".join(f"- {r}" for r in remarks)

    # Extract uncertainty of measurement
    uom_match = re.search(
        r'UNCERTAINTY OF MEASUREMENT:\s*(.*?)(?=\n[A-Z ]+?:|\nPage\s*\d+\s*of\s*\d+)',
        raw_text,
        re.DOTALL
    )
    if uom_match:
        info['uncertainty_of_measurement'] = uom_match.group(1).strip()
    else:
        info['uncertainty_of_measurement'] = ''

    # Clean up data
    for key, val
personnel_label = CTkLabel(master=scrollable_frame, text="Personnel:", font=("Inter", 14, "bold"), bg_color='white')
personnel_label.grid(row=25, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

# Analyst # 1 Label
analyst1_label = CTkLabel(master=scrollable_frame, text="Analyst # 1:", font=("Inter", 12, "bold"), bg_color='white')
analyst1_label.grid(row=26, column=0, padx=10, pady=(5, 5), sticky="w")

# Analyst # 1 Textbox
analyst1_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. John Doe")
analyst1_textbox.grid(row=27, column=0, padx=10, pady=(5, 10), sticky="w")

# Role Label
role1_label = CTkLabel(master=scrollable_frame, text="Role:", font=("Inter", 12, "bold"), bg_color='white')
role1_label.grid(row=26, column=1, padx=10, pady=(5, 5), sticky="w")

# Role Textbox
role1_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. Science Research Specialist II")
role1_textbox.grid(row=27, column=1, padx=10, pady=(5, 10), sticky="w")

# Analyst # 2 Label
analyst2_label = CTkLabel(master=scrollable_frame, text="Analyst # 2:", font=("Inter", 12, "bold"), bg_color='white')
analyst2_label.grid(row=28, column=0, padx=10, pady=(5, 5), sticky="w")

# Analyst # 2 Textbox
analyst2_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. Jane Smith")
analyst2_textbox.grid(row=29, column=0, padx=10, pady=(5, 10), sticky="w")

# Role Label
role2_label = CTkLabel(master=scrollable_frame, text="Role:", font=("Inter", 12, "bold"), bg_color='white')
role2_label.grid(row=28, column=1, padx=10, pady=(5, 5), sticky="w")

# Role Textbox
role2_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. Senior Science Research Specialist")
role2_textbox.grid(row=29, column=1, padx=10, pady=(5, 10), sticky="w")

# Authorized by Label
authorized_label = CTkLabel(master=scrollable_frame, text="Authorized by:", font=("Inter", 12, "bold"), bg_color='white')
authorized_label.grid(row=30, column=0, padx=10, pady=(5, 5), sticky="w")

# Authorized by Textbox
authorized_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. Maria Santos")
authorized_textbox.grid(row=31, column=0, padx=10, pady=(5, 10), sticky="w")

# Role Label
authorized_role_label = CTkLabel(master=scrollable_frame, text="Role:", font=("Inter", 12, "bold"), bg_color='white')
authorized_role_label.grid(row=30, column=1, padx=10, pady=(5, 5), sticky="w")

# Role Textbox
authorized_role_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. Head, Pressure and Force Standards Section")
authorized_role_textbox.grid(row=31, column=1, padx=10, pady=(5, 10), sticky="w")

############################
# Customer Information Label
customer_info_label = CTkLabel(master=scrollable_frame, text="Customer Information:", font=("Inter", 14, "bold"), bg_color='white')
customer_info_label.grid(row=32, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

# Customer Label
customer_label = CTkLabel(master=scrollable_frame, text="Customer:", font=("Inter", 12, "bold"), bg_color='white')
customer_label.grid(row=33, column=0, padx=10, pady=(5, 5), sticky="w")

# Customer Textbox
customer_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. ABC Corporation")
customer_textbox.grid(row=34, column=0, padx=10, pady=(5, 10), sticky="w")

# Address Label
address_label = CTkLabel(master=scrollable_frame, text="Address:", font=("Inter", 12, "bold"), bg_color='white')
address_label.grid(row=33, column=1, padx=10, pady=(5, 5), sticky="w")

# Address Textbox
address_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. 123 Main St, City, Country")
address_textbox.grid(row=34, column=1, padx=10, pady=(5, 10), sticky="w")

################################
# Environmental Conditions Label
environmental_conditions_label = CTkLabel(master=scrollable_frame, text="Environmental Conditions:", font=("Inter", 14, "bold"), bg_color='white')
environmental_conditions_label.grid(row=35, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

# Temperature Label
temperature_label = CTkLabel(master=scrollable_frame, text="Temperature:", font=("Inter", 12, "bold"), bg_color='white')
temperature_label.grid(row=36, column=0, padx=10, pady=(5, 5), sticky="w")

# Temperature Textbox
temperature_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. (22 ± 2)")
temperature_textbox.grid(row=37, column=0, padx=10, pady=(5, 10), sticky="w")

# Unit Label (Temperature)
temperature_unit_label = CTkLabel(master=scrollable_frame, text="Unit:", font=("Inter", 12, "bold"), bg_color='white')
temperature_unit_label.grid(row=36, column=1, padx=10, pady=(5, 5), sticky="w")

# Unit Textbox (Temperature)
temperature_unit_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. \celcius")
temperature_unit_textbox.grid(row=37, column=1, padx=10, pady=(5, 10), sticky="w")

# Humidity Label
humidity_label = CTkLabel(master=scrollable_frame, text="Humidity:", font=("Inter", 12, "bold"), bg_color='white')
humidity_label.grid(row=38, column=0, padx=10, pady=(5, 5), sticky="w")

# Humidity Textbox
humidity_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. (40 ± 5)")
humidity_textbox.grid(row=39, column=0, padx=10, pady=(5, 10), sticky="w")

# Unit Label (Humidity)
humidity_unit_label = CTkLabel(master=scrollable_frame, text="Unit:", font=("Inter", 12, "bold"), bg_color='white')
humidity_unit_label.grid(row=38, column=1, padx=10, pady=(5, 5), sticky="w")

# Unit Textbox (Humidity)
humidity_unit_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. \%")
humidity_unit_textbox.grid(row=39, column=1, padx=10, pady=(5, 10), sticky="w")

##########################
# Results Label
results_label = CTkLabel(master=scrollable_frame, text="Results:", font=("Inter", 14, "bold"), bg_color='white')
results_label.grid(row=40, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

# Applied Force Label
applied_force_label = CTkLabel(master=scrollable_frame, text="Applied Force:", font=("Inter", 12, "bold"), bg_color='white')
applied_force_label.grid(row=41, column=0, padx=10, pady=(5, 5), sticky="w")

# Applied Force Textbox
applied_force_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. 0.00 3 000 6 000")
applied_force_textbox.grid(row=42, column=0, padx=10, pady=(5, 10), sticky="w")

# Unit Label (Applied Force)
applied_force_unit_label = CTkLabel(master=scrollable_frame, text="Unit:", font=("Inter", 12, "bold"), bg_color='white')
applied_force_unit_label.grid(row=41, column=1, padx=10, pady=(5, 5), sticky="w")

# Unit Textbox (Applied Force)
applied_force_unit_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. \kgf \kgf \kgf")
applied_force_unit_textbox.grid(row=42, column=1, padx=10, pady=(5, 10), sticky="w")

# Indicated Force Label
indicated_force_label = CTkLabel(master=scrollable_frame, text="Indicated Force:", font=("Inter", 12, "bold"), bg_color='white')
indicated_force_label.grid(row=43, column=0, padx=10, pady=(5, 5), sticky="w")

# Indicated Force Textbox
indicated_force_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. 0.00 2 850 5 700")
indicated_force_textbox.grid(row=44, column=0, padx=10, pady=(5, 10), sticky="w")

# Unit Label (Indicated Force)
indicated_force_unit_label = CTkLabel(master=scrollable_frame, text="Unit:", font=("Inter", 12, "bold"), bg_color='white')
indicated_force_unit_label.grid(row=43, column=1, padx=10, pady=(5, 5), sticky="w")

# Unit Textbox (Indicated Force)
indicated_force_unit_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. \kgf \kgf \kgf")
indicated_force_unit_textbox.grid(row=44, column=1, padx=10, pady=(5, 10), sticky="w")

# Relative Expanded Uncertainty Label
relative_expandedUn_label = CTkLabel(master=scrollable_frame, text="Relative Measurement Error:", font=("Inter", 12, "bold"), bg_color='white')
relative_expandedUn_label.grid(row=45, column=0, padx=10, pady=(5, 5), sticky="w")

# Relative Expanded Uncertainty Textbox
relative_expandedUn_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. 0.00 1.04 0.56")
relative_expandedUn_textbox.grid(row=46, column=0, padx=10, pady=(5, 10), sticky="w")

# Unit Label (Relative Expanded Uncertainty)
relative_expandedUn_unit_label = CTkLabel(master=scrollable_frame, text="Unit:", font=("Inter", 12, "bold"), bg_color='white')
relative_expandedUn_unit_label.grid(row=45, column=1, padx=10, pady=(5, 5), sticky="w")

# Unit Textbox (Relative Expanded Uncertainty)
relative_expandedUn_unit_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. \% \% \%")
relative_expandedUn_unit_textbox.grid(row=46, column=1, padx=10, pady=(5, 10), sticky="w")

#############################
# Calibration Procedure Label
calibration_procedure_label = CTkLabel(master=scrollable_frame, text="Calibration Procedure:", font=("Inter", 14, "bold"), bg_color='white')
calibration_procedure_label.grid(row=47, column=0, padx=10, pady=(5, 5), sticky="w")

# Define placeholder text and color
placeholder_text = "e.g. CALIBRATION PROCEDURE: The axle weighing scale was subjected to specified..."

def on_focus_in(event):
    current_text = calibration_procedure_textbox.get("1.0", "end-1c")
    if current_text == placeholder_text:
        calibration_procedure_textbox.delete("1.0", "end")
        calibration_procedure_textbox.configure(text_color="black")

def on_focus_out(event):
    current_text = calibration_procedure_textbox.get("1.0", "end-1c").strip()
    if current_text == "":
        calibration_procedure_textbox.insert("1.0", placeholder_text)
        calibration_procedure_textbox.configure(text_color="gray")

# Calibration Procedure Textbox (Multiline with wrapping)
calibration_procedure_textbox = CTkTextbox(
    master=scrollable_frame,
    font=("Inter", 12),
    fg_color='white',
    text_color="gray",
    border_width=2,
    height=90,
    wrap='word'
)
calibration_procedure_textbox.insert("1.0", placeholder_text)
calibration_procedure_textbox.bind("<FocusIn>", on_focus_in)
calibration_procedure_textbox.bind("<FocusOut>", on_focus_out)
calibration_procedure_textbox.grid(row=48, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="we")


###############
# Remarks Label
remarks_label = CTkLabel(master=scrollable_frame, text="Remarks:", font=("Inter", 14, "bold"), bg_color='white')
remarks_label.grid(row=49, column=0, padx=10, pady=(5, 5), sticky="w")

# Define placeholder text and color
remarks_placeholder = "e.g. REMARKS: - The above results were those obtained at the time of calibration..."

def on_remarks_focus_in(event):
    current_text = remarks_textbox.get("1.0", "end-1c")
    if current_text == remarks_placeholder:
        remarks_textbox.delete("1.0", "end")
        remarks_textbox.configure(text_color="black")

def on_remarks_focus_out(event):
    current_text = remarks_textbox.get("1.0", "end-1c").strip()
    if current_text == "":
        remarks_textbox.insert("1.0", remarks_placeholder)
        remarks_textbox.configure(text_color="gray")

# Remarks Textbox with placeholder behavior
remarks_textbox = CTkTextbox(
    master=scrollable_frame,
    font=("Inter", 12),
    fg_color='white',
    text_color="gray",  # start as placeholder
    border_width=2,
    height=90,
    wrap='word'
)
remarks_textbox.insert("1.0", remarks_placeholder)
remarks_textbox.bind("<FocusIn>", on_remarks_focus_in)
remarks_textbox.bind("<FocusOut>", on_remarks_focus_out)
remarks_textbox.grid(row=50, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="we")


# ^ content of scrollable frame
#########################################

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load and Resize the Image
itdi_logo_path = os.path.join(script_dir, "itdi-logo.png")
image = CTkImage(light_image=Image.open(itdi_logo_path), size=(26, 25))
# Create CTkLabel with Image
image_label = CTkLabel(master=app, image=image, text="", bg_color='white') 
image_label.place(relx=0.4525, rely=0.0457)

# Load and Resize the Image
nml_logo_path = os.path.join(script_dir, "nml-logo1.png")
image1 = CTkImage(light_image=Image.open(nml_logo_path), size=(29, 28))
# Create CTkLabel with Image
image_label = CTkLabel(master=app, image=image1, text="", bg_color='white') 
image_label.place(relx=0.4225, rely=0.0457)

stroke = CTkFrame(master=app, fg_color="#0855B1", corner_radius=0)
stroke.place(relx=0.0483, rely=0.0438, relwidth=0.006, relheight=0.045)

# Title label
titleLabel = CTkLabel(master=app, text="DigiCert", font=("Montserrat", 32, "bold"), bg_color='white')
titleLabel.place(relx=0.0567, rely=0.0330)

# BG rectangle 1
bg_frame = CTkFrame(master=app, fg_color="#E0E0E0", corner_radius=0)
bg_frame.place(relx=0.5, rely=0.0, relwidth=0.5, relheight=1.0)

# BG rectangle 
footer_frame = CTkFrame(master=app, fg_color="#E0E0E0", corner_radius=0)
footer_frame.place(relx=0.0, rely=0.89, relwidth=0.5, relheight=0.1114)

# Save Edit button
saveEButton = CTkButton(master=app, text="Save Edit", corner_radius=7, 
                       fg_color="#000000", hover_color="#1A4F8B", font=("Inter", 13))
saveEButton.place(relx=0.1417, rely=0.9220, relwidth=0.1008, relheight=0.0471)

# Export button
exportButton = CTkButton(master=app, text="Export", corner_radius=7, 
                         fg_color="#010E54", hover_color="#1A4F8B", font=("Inter", 13))
exportButton.place(relx=0.2575, rely=0.9220, relwidth=0.1008, relheight=0.0471)

# Back button
backButton = CTkButton(master=app, text="< ", corner_radius=7, 
                    fg_color="#010E54", hover_color="#1A4F8B", font=("Inter", 15))
backButton.place(relx=0.0225, rely=0.0486, relwidth=0.0200, relheight=0.0350)

# PDF to XML label
titleLabel = CTkLabel(master=app, text="PDF -> XML", font=("Inter", 13, "bold"), bg_color='white')
titleLabel.place(relx=0.1800, rely=0.0514)

##########################
# insert code for the preview of XML file here

xml_preview = CTkTextbox(master=app, font=("Courier", 12), wrap="none")
xml_preview.place(relx=0.6, rely=0.24, relwidth=0.35, relheight=0.65)


def preload_xml(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            raw_xml = f.read()
            try:
                parsed_xml = xml.dom.minidom.parseString(raw_xml)
                pretty_xml = parsed_xml.toprettyxml(indent="  ")
            except Exception as e:
                pretty_xml = f"Error parsing XML:\n{e}"

            xml_preview.delete("0.0", "end")
            xml_preview.insert("0.0", pretty_xml)

# Use the absolute path for the XML template too
template_path = os.path.join(script_dir, "template.xml")
preload_xml(template_path)  # Use absolute path for template



preload_xml("template.xml")  # Replace with the actual path of your template



app.mainloop()