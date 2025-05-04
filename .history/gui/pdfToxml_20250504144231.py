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
    for key, val in info.items():
        if isinstance(val, str):
            info[key] = re.sub(r'\s+', ' ', val).strip()
            info[key] = info[key].replace(' ,', ',').replace(' .', '.')
            info[key] = info[key].replace(' ;', ';').replace(' :', ':')
    
    return info

# Process PDF file if provided as command line argument
pdf_path = None
calibration_info = {}
table_columns = []
if len(sys.argv) > 1:
    pdf_path = sys.argv[1]
    try:
        # Extract text and tables from PDF
        raw_text = extract_text(pdf_path)
        table_columns = extract_table_columns(pdf_path)
        
        # Process extracted data
        calibration_info = extract_calibration_info(raw_text)
        
        # Process tables for additional information
        if len(table_columns) > 1:
            # Extract instrument name and serial number from Table 2
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

            # Extract measurement results from table 1
            if len(table_columns) > 0:
                # Extract standard measurement
                standard_measurement = list(table_columns[0].keys())[0]
                raw_standard = table_columns[0][standard_measurement]
                standard_unit = raw_standard[0]
                raw_standard_str = raw_standard[1]
                standard_val = raw_standard_str.replace('\n', ' ')

                # Extract equipment measured values
                measured_col = next((col for col in table_columns[0]
                                    if 'indicated' in col.lower()), None)
                if measured_col:
                    raw_measured = table_columns[0][measured_col]
                    measured_unit = raw_measured[0]
                    measured_val = raw_measured[1].replace('\n', ' ')
                else:
                    measured_unit = ''
                    measured_val = ''

                # Extract uncertainty values
                uncertainty_col = ""
                for col_name, col_values in table_columns[0].items():
                    if 'uncertainty' in col_name.lower():
                        uncertainty_col = col_name
                        break

                if uncertainty_col:
                    raw_uncertainty = table_columns[0][uncertainty_col]
                    uncertainty_unit = raw_uncertainty[0]
                    uncertainty_str = raw_uncertainty[1]
                    value_count = uncertainty_str.count('\n') + 1
                    uncertainty_val = uncertainty_str.replace('\n', ' ')

                    # Store extracted values in calibration_info
                    calibration_info['standard_item'] = instrument_name
                    calibration_info['standard_serial_number'] = instrument_serial
                    calibration_info['standard_model'] = make_model
                    calibration_info['standard_cert_number'] = cert_number
                    calibration_info['standard_traceability'] = traceability
                    calibration_info['relative_uncertainty'] = uncertainty_col.replace('\n', ' ')
                    calibration_info['relative_uncertainty_unit'] = uncertainty_unit
                    calibration_info['relative_uncertainty_values'] = uncertainty_val
                    calibration_info['value_count'] = value_count
                    calibration_info['standard_measurement'] = standard_measurement.replace('\n', ' ')
                    calibration_info['standard_measurement_unit'] = standard_unit
                    calibration_info['standard_measurement_values'] = standard_val
                    calibration_info['measured_item'] = measured_col.replace('\n', ' ') if measured_col else ''
                    calibration_info['measured_item_unit'] = measured_unit
                    calibration_info['measured_item_values'] = measured_val
    except Exception as e:
        print(f"Error processing PDF: {e}")

# Initialize the GUI
app = CTk()
app.title("DigiCert")
app.geometry("1200x700")
set_appearance_mode("light")

# Rest of your GUI code follows
# [rest of the code continues unchanged]
