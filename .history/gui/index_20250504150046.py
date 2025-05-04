from customtkinter import *
from PIL import Image
import os
from PIL import Image
import subprocess
import sys
import pdfplumber
import re
from datetime import datetime
from lxml import etree as LET



app = CTk()
app.title("DigiCert")
app.geometry("500x500") 
set_appearance_mode("light")

# Disable maximize button
app.resizable(False, False)

# Create a CTkFrame to act as the background (canvas)
bg_frame = CTkFrame(master=app, fg_color="white")  # Set the color to white
bg_frame.place(relx=0, rely=0, relwidth=1, relheight=1)  # Fill the entire window

# Functions
def open_cert():
    filename = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg")])
    global img_path
    img_path = filename
    certLabel.configure(text=os.path.basename(filename))
    return filename

def open_format():
        # only look for PDF now
        filename = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")]
        )
        if not filename:
            return
        global pdf_path
        pdf_path = filename
        formatLabel.configure(text=os.path.basename(filename))
        # Pass the selected PDF file path to pdfToxml.py
        subprocess.Popen(["python", "gui/pdfToxml.py", pdf_path])
        app.destroy()  # Close the current app window after launching the next script
        return filename

def open_newxml_gui():
    app.destroy()  # Close the current app window
    subprocess.Popen(["python", "new-xml.py"])

def open_settings():
    app.destroy()  # Close the current app window
    subprocess.Popen(["python", "settings.py"])

def pdfToxml():
    import xml.etree.ElementTree as ET
    
    # Get the PDF path from sys.argv
    pdf_path = sys.argv[1]
    
    # Extract text from PDF
    def extract_text(path):
        with pdfplumber.open(path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    
    # Extract table data from PDF
    def extract_table_columns(path):
        tables_columns = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if not table or len(table) < 2:
                        continue
                    headers = table[0]
                    columns_data = {}
                    for header in headers:
                        if header:
                            columns_data[header] = []
                    for row in table[1:]:
                        for i, cell in enumerate(row):
                            if i < len(headers) and headers[i] and cell:
                                columns_data[headers[i]].append(cell)
                    tables_columns.append(columns_data)
        return tables_columns
    
    # Extract calibration information
    def extract_calibration_info(raw_text):
        # Initialize dictionary for storing extracted info
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
        
        # Extract data using regex patterns
        lines = raw_text.split('\n')
        
        # Certificate number
        cert_match = re.search(r'No\.\s+([\w\-]+)', raw_text)
        if cert_match:
            info['certificate_number'] = cert_match.group(1)
        
        # Calibration date
        date_match = re.search(r'Date of Calibration\s*:\s*([^\n]+)', raw_text)
        if date_match:
            info['calibration_date'] = date_match.group(1).strip()
        
        # Calibration item
        item_match = re.search(r'Calibration Item\s*:\s*([^\n]+)', raw_text)
        if item_match:
            info['calibration_item'] = item_match.group(1).strip()
        
        # Other fields extraction
        for field, pattern in [
            ('capacity', r'Capacity\s*:\s*([^\n]+)'),
            ('measurement_range', r'Measurement Range\s*:\s*([^\n]+)'),
            ('resolution', r'Resolution\s*:\s*([^\n]+)'),
            ('make_model', r'Make / Model\s*:\s*([^\n]+)'),
            ('serial_number', r'Serial No\.\s*:\s*([^\n]+)'),
            ('temperature', r'Ambient Temperature\s*:\s*\(?([^\)\n]+)\)?'),
            ('humidity', r'Relative Humidity\s*:\s*\(?([^\)\n]+)\)?')
        ]:
            match = re.search(pattern, raw_text)
            if match:
                info[field] = match.group(1).strip()
        
        # Customer information
        customer_match = re.search(r'Customer\s*:\s*([^\n]+)', raw_text)
        if customer_match:
            info['customer_name'] = customer_match.group(1).strip()
            
            # Find customer address
            customer_line_index = -1
            for i, line in enumerate(lines):
                if 'Customer :' in line or 'Customer:' in line:
                    customer_line_index = i
                    break
            
            if customer_line_index != -1 and customer_line_index + 1 < len(lines):
                address_line = lines[customer_line_index + 1].strip()
                if address_line and not address_line.isupper() and 'MEASUREMENT' not in address_line:
                    info['customer_address'] = address_line
        
        # Extract responsible persons
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

        for idx, li in enumerate(person_indices[:3]):
            info[f'resp_person{idx+1}_name'] = lines[li].strip()
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
        
        # Extract remarks
        remarks = []
        in_remarks = False
        current_remark = ""
        for line in lines:
            stripped = line.strip()
            if not in_remarks:
                if stripped.startswith("REMARKS"):
                    in_remarks = True
                continue
            if (stripped.isupper() and not stripped.startswith("-")) or re.match(r'^[A-Z\s]+:$', stripped):
                break
            if stripped.startswith("-"):
                if current_remark:
                    remarks.append(current_remark.strip())
                current_remark = stripped.lstrip("- ").strip()
            elif current_remark:
                current_remark += " " + stripped
        
        if current_remark:
            remarks.append(current_remark.strip())
        
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
    
    # Extract text and tables from PDF
    raw_text = extract_text(pdf_path)
    table_columns = extract_table_columns(pdf_path)
    calibration_info = extract_calibration_info(raw_text)
    
    # Process data from tables
    if len(table_columns) > 1:
        # Extract instrument info from Table 2
        std_entry = table_columns[1]['Name of Standard'][0]
        lines = std_entry.split('\n')
        instrument_name = ' '.join(lines[:-1]).strip()
        instrument_serial = lines[-1].strip()
        make_model = " ".join(table_columns[1]['Make/Model'][0].split())
        cert_number = table_columns[1]['Calibration Certificate No.'][0]
        traceability = " ".join(table_columns[1]['Traceability'][0].split())
        
        # Process measurement results table
        standard_measurement = list(table_columns[0].keys())[0]
        raw_standard = table_columns[0][standard_measurement]
        standard_unit = raw_standard[0]
        raw_standard_str = raw_standard[1]
        standard_val = raw_standard_str.replace('\n', ' ')
        
        # Extract measured values
        measured_col = next((col for col in table_columns[0] if 'indicated' in col.lower()), None)
        if measured_col:
            raw_measured = table_columns[0][measured_col]
            measured_unit = raw_measured[0]
            measured_val = raw_measured[1].replace('\n', ' ')
        else:
            measured_unit = ''
            measured_val = ''
        
        # Find uncertainty column
        uncertainty_col = ""
        for col_name, col_values in table_columns[0].items():
            if 'uncertainty' in col_name.lower():
                uncertainty_col = col_name
                break
        
        raw_uncertainty = table_columns[0][uncertainty_col]
        uncertainty_unit = raw_uncertainty[0]
        uncertainty_str = raw_uncertainty[1]
        value_count = uncertainty_str.count('\n') + 1
        uncertainty_val = uncertainty_str.replace('\n', ' ')
        
        # Update calibration_info with extracted data
        calibration_info.update({
            'standard_item': instrument_name,
            'standard_serial_number': instrument_serial,
            'standard_model': make_model,
            'standard_cert_number': cert_number,
            'standard_traceability': traceability,
            'relative_uncertainty': uncertainty_col.replace('\n', ' '),
            'relative_uncertainty_unit': uncertainty_unit,
            'relative_uncertainty_values': uncertainty_val,
            'value_count': value_count,
            'standard_measurement': standard_measurement.replace('\n', ' '),
            'standard_measurement_unit': standard_unit,
            'standard_measurement_values': standard_val,
            'measured_item': measured_col.replace('\n', ' ') if measured_col else '',
            'measured_item_unit': measured_unit,
            'measured_item_values': measured_val
        })
    
    # Generate XML file
    # Define variables for XML
    software_name = "DigiCert"
    software_release = "v0.0"
    country_code_iso = "PH"
    used_lang_code = "en"
    mandatory_lang_code = "en"
    unique_identifier = "Calibration No. " + calibration_info["certificate_number"]
    
    # Process date
    raw_date = calibration_info.get("calibration_date", "")
    step1 = re.sub(r"([A-Za-z]+)(\d)", r"\1 \2", raw_date)
    step2 = step1.replace(",", ", ")
    norm = re.sub(r"\s+", " ", step2).strip()
    try:
        dt = datetime.strptime(norm, "%B %d, %Y")
        begin_performance_date = dt.strftime("%Y-%m-%d")
    except ValueError:
        begin_performance_date = ""
    
    # Additional XML data
    end_performance_date = ""
    performance_location = "LABORATORY"
    
    # Set up XML template and namespaces
    template = r"valid xml\template.xml"
    output = r"valid xml\filled.xml"
    ns = {"dcc":"https://ptb.de/dcc", "si":"https://ptb.de/si"}
    
    for p, u in ns.items():
        ET.register_namespace(p, u)
    
    # Try to parse the template
    try:
        tree = ET.parse(template)
    except ET.ParseError:
        try:
            parser = LET.XMLParser(recover=True)
            tree = LET.parse(template, parser)
        except ImportError:
            print("Error parsing template. Install lxml for better error recovery.")
            return
    
    root = tree.getroot()
    
    # Helper function to set element text
    def set_text(elem, txt, lang=None):
        if elem is None or txt is None:
            return
        elem.text = txt
        if lang:
            elem.set("lang", lang)
    
    # Fill in XML data
    # 1) Software
    sw = root.find(".//dcc:software", ns)
    set_text(sw.find("dcc:name/dcc:content", ns), software_name)
    set_text(sw.find("dcc:release", ns), software_release)
    
    # 2) Core data
    cd = root.find(".//dcc:coreData", ns)
    set_text(cd.find("dcc:countryCodeISO3166_1", ns), country_code_iso)
    set_text(cd.find("dcc:usedLangCodeISO639_1", ns), used_lang_code)
    set_text(cd.find("dcc:mandatoryLangCodeISO639_1", ns), mandatory_lang_code)
    set_text(cd.find("dcc:uniqueIdentifier", ns), unique_identifier)
    set_text(cd.find("dcc:beginPerformanceDate", ns), begin_performance_date)
    set_text(cd.find("dcc:endPerformanceDate", ns), end_performance_date)
    set_text(cd.find("dcc:performanceLocation", ns), performance_location)
    
    # 3) Items: calibration item and standard
    items = root.findall(".//dcc:items/dcc:item", ns)
    
    # Calibration item
    if items:
        ci = items[0]
        set_text(ci.find("dcc:name/dcc:content", ns), calibration_info.get("calibration_item", ""), lang=used_lang_code)
        set_text(ci.find("dcc:manufacturer/dcc:name/dcc:content", ns), "", lang=used_lang_code)
        set_text(ci.find("dcc:model", ns), calibration_info["make_model"])
        
        ident = ci.find("dcc:identifications/dcc:identification", ns)
        if ident is not None:
            set_text(ident.find("dcc:issuer", ns), "customer")
            set_text(ident.find("dcc:value", ns), calibration_info["calibration_item"])
            set_text(ident.find("dcc:name/dcc:content", ns), calibration_info["serial_number"], lang=used_lang_code)
        
        desc = ci.find("dcc:description", ns)
        if desc is not None:
            cont = desc.findall("dcc:content", ns)
            if len(cont) > 0:
                set_text(cont[0], "Capacity: " + calibration_info["capacity"], lang=used_lang_code)
            if len(cont) > 1:
                set_text(cont[1], "Measurement Range: " + calibration_info["measurement_range"], lang=used_lang_code)
            if len(cont) > 2:
                set_text(cont[2], "Resolution: " + calibration_info["resolution"], lang=used_lang_code)
    
    # Standard item
    if len(items) > 1:
        si_el = items[1]
        set_text(si_el.find("dcc:name/dcc:content", ns), calibration_info["standard_item"], lang=used_lang_code)
        set_text(si_el.find("dcc:manufacturer/dcc:name/dcc:content", ns), "", lang=used_lang_code)
        set_text(si_el.find("dcc:model", ns), calibration_info["standard_model"])
        
        ident2 = si_el.find("dcc:identifications/dcc:identification", ns)
        if ident2 is not None:
            set_text(ident2.find("dcc:issuer", ns), "LABORATORY")
            set_text(ident2.find("dcc:value", ns), calibration_info["standard_serial_number"])
            set_text(ident2.find("dcc:name/dcc:content", ns), calibration_info["standard_item"], lang=used_lang_code)
        
        desc2 = si_el.find("dcc:description", ns)
        if desc2 is not None:
            cont2 = desc2.findall("dcc:content", ns)
            if len(cont2) > 0:
                set_text(cont2[0], "Calibration Certificate No.: " + calibration_info["standard_cert_number"], lang=used_lang_code)
            if len(cont2) > 1:
                set_text(cont2[1], "Traceability: " + calibration_info["standard_traceability"], lang=used_lang_code)
    
    # 4) Calibration laboratory
    lab = root.find(".//dcc:calibrationLaboratory", ns)
    set_text(lab.find("dcc:calibrationLaboratoryCode", ns), "FORC")
    set_text(lab.find("dcc:contact/dcc:name/dcc:content", ns), 
             "National Metrology Laboratory - Industrial Technology Development Institute", lang=used_lang_code)
    
    loc = lab.find("dcc:contact/dcc:location", ns)
    set_text(loc.find("dcc:city", ns), "Taguig")
    set_text(loc.find("dcc:countryCode", ns), "PH")
    set_text(loc.find("dcc:postCode", ns), "1633")
    set_text(loc.find("dcc:street", ns), "General Santos Ave")
    
    # 5) Responsible persons
    resp_nodes = root.findall(".//dcc:respPersons/dcc:respPerson", ns)
    resp_data = [
        (calibration_info.get("resp_person1_name", ""), calibration_info.get("resp_person1_role", "")),
        (calibration_info.get("resp_person2_name", ""), calibration_info.get("resp_person2_role", "")),
        (calibration_info.get("resp_person3_name", ""), calibration_info.get("resp_person3_role", ""))
    ]
    
    for idx, (name, role) in enumerate(resp_data):
        if idx < len(resp_nodes) and name and role:
            rp = resp_nodes[idx]
            set_text(rp.find("dcc:person/dcc:name/dcc:content", ns), name, lang=used_lang_code)
            set_text(rp.find("dcc:role", ns), role)
    
    # 6) Customer
    cust = root.find(".//dcc:customer", ns)
    set_text(cust.find("dcc:name/dcc:content", ns), calibration_info["customer_name"])
    f = cust.find("dcc:location/dcc:further/dcc:content", ns)
    set_text(f, calibration_info.get("customer_address", ""), lang=used_lang_code)
    
    # 7) Measurement results
    mr = root.find(".//dcc:measurementResults", ns)
    set_text(mr.find("dcc:name/dcc:content", ns), calibration_info["calibration_item"], lang=used_lang_code)
    
    um = mr.find("dcc:usedMethods/dcc:usedMethod", ns)
    set_text(um.find("dcc:name/dcc:content", ns), calibration_info["relative_uncertainty"], lang=used_lang_code)
    set_text(um.find("dcc:description/dcc:content", ns), calibration_info["uncertainty_of_measurement"], lang=used_lang_code)
    
    # Influence conditions
    ic = mr.find(".//dcc:influenceConditions", ns)
    if ic is not None:
        conds = ic.findall("dcc:influenceCondition", ns)
        
        # Temperature
        if len(conds) > 0:
            infl = conds[0]
            set_text(infl.find("dcc:name/dcc:content", ns), "Ambient Temperature", lang=used_lang_code)
            dq = infl.find(".//dcc:quantity", ns)
            set_text(dq.find("dcc:name/dcc:content", ns), "Ambient Temperature", lang=used_lang_code)
            real = dq.find("si:real", ns)
            set_text(real.find("si:value", ns), calibration_info.get("temperature", ""))
            set_text(real.find("si:unit", ns), "\\°C")
        
        # Humidity
        if len(conds) > 1:
            infl = conds[1]
            set_text(infl.find("dcc:name/dcc:content", ns), "Relative Humidity", lang=used_lang_code)
            dq = infl.find(".//dcc:quantity", ns)
            set_text(dq.find("dcc:name/dcc:content", ns), "Relative Humidity", lang=used_lang_code)
            real = dq.find("si:real", ns)
            set_text(real.find("si:value", ns), calibration_info.get("humidity", ""))
            set_text(real.find("si:unit", ns), "\\%")
    
    # Results
    res = mr.find(".//dcc:results", ns)
    if res is not None:
        names = [
            calibration_info["standard_measurement"],
            calibration_info.get("measured_item", ""),
            calibration_info["relative_uncertainty"]
        ]
        values = [
            calibration_info["standard_measurement_values"],
            calibration_info.get("measured_item_values", ""),
            calibration_info["relative_uncertainty_values"]
        ]
        
        std_unit = calibration_info["standard_measurement_unit"]
        meas_unit = calibration_info.get("measured_item_unit", "")
        unc_unit = calibration_info["relative_uncertainty_unit"]
        value_count = calibration_info.get("value_count", 1)
        
        units = [
            ' '.join([f'\\{std_unit}'] * value_count),
            ' '.join([f'\\{meas_unit}'] * value_count),
            ' '.join([f'\\{unc_unit}'] * value_count)
        ]
        
        for idx, row in enumerate(res.findall("dcc:result", ns)):
            if idx < 3:  # Ensure we don't exceed available rows
                set_text(row.find("dcc:name/dcc:content", ns), names[idx], lang=used_lang_code)
                real_list = row.find(".//si:realListXMLList", ns)
                if real_list is not None:
                    set_text(real_list.find("si:valueXMLList", ns), values[idx])
                    set_text(real_list.find("si:unitXMLList", ns), units[idx])
    
    # 8) Comment
    comm = root.find(".//dcc:comment", ns)
    cc = comm.findall("dcc:content", ns)
    if cc:
        set_text(cc[0], "CALIBRATION PROCEDURE: " + calibration_info["calibration_procedure"], lang=used_lang_code)
    if len(cc) > 1:
        set_text(cc[1], "REMARKS: " + calibration_info["remarks"], lang=used_lang_code)
    
    # Write the XML file
    tree.write(output, encoding="utf-8", xml_declaration=True)
    
    print(f"Successfully created XML file at {output}")
   


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
                    fg_color="#0855B1", hover_color="#010E54", font=("Inter", 13),command=open_cert)
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
                    fg_color="#0855B1", hover_color="#010E54", font=("Inter", 13),command=open_format)
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