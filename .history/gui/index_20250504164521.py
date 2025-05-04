from tkinter import messagebox
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
    global output
    pdf_path = filename
    formatLabel.configure(text=os.path.basename(filename))
    
    try: 
        # Call the pdf_to_xml function with the selected PDF 
        output = pdf_to_xml(pdf_path)
        if output:
            messagebox.showinfo("Success", f"XML file created successfully at: {output}")
            # Close the current app window and open pdfToxml.py with the output file path
            app.destroy()
            subprocess.Popen(["python", "pdfToxml.py", output])  # Pass the output file path as an argument
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
       

def open_newxml_gui():
    app.destroy()  # Close the current app window
    subprocess.Popen(["python", "new-xml.py"])

def open_settings():
    app.destroy()  # Close the current app window
    subprocess.Popen(["python", "settings.py"])

def pdf_to_xml(pdf_path):
    # This function is a placeholder for the actual PDF to XML conversion logic.
    # You can implement the conversion logic here.
     # Process the PDF to XML
        import re
        import pdfplumber
        import xml.etree.ElementTree as ET
        from datetime import datetime
        
        # Set output path
        template = r"valid xml\template.xml"
        
        
        # Extract text from PDF
        def extract_text(path):
            with pdfplumber.open(path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        
        # Extract table data from PDF
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
        
        # Extract calibration information
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

            # Extract uncertainty of measurement narrative
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
            for key in info:
                if isinstance(info[key], str):
                    info[key] = re.sub(r'\s+', ' ', info[key]).strip()
                    # Fix specific formatting issues
                    info[key] = info[key].replace(' ,', ',').replace(' .', '.')
                    info[key] = info[key].replace(' ;', ';').replace(' :', ':')
            
            return info
        
        # Process the PDF
        raw_text = extract_text(pdf_path)
        table_columns = extract_table_columns(pdf_path)
        calibration_info = extract_calibration_info(raw_text)
        
        # Extract additional info from tables
        if len(table_columns) >= 2:
            # Extract from standard table (table 2)
            std_entry = table_columns[1]['Name of Standard'][0]
            lines = std_entry.split('\n')
            instrument_name = ' '.join(lines[:-1]).strip()
            instrument_serial = lines[-1].strip()
            make_model = " ".join(table_columns[1]['Make/Model'][0].split())
            cert_number = table_columns[1]['Calibration Certificate No.'][0]
            traceability = " ".join(table_columns[1]['Traceability'][0].split())
            
            # Extract from measurements table (table 1)
            standard_measurement = list(table_columns[0].keys())[0]
            raw_standard = table_columns[0][standard_measurement]
            standard_unit = raw_standard[0]
            raw_standard_str = raw_standard[1]
            standard_val = raw_standard_str.replace('\n', ' ')
            
            # Extract equipment measurements
            measured_col = next((col for col in table_columns[0]
                              if 'indicated' in col.lower()), None)
            if measured_col:
                raw_measured = table_columns[0][measured_col]
                measured_unit = raw_measured[0]
                measured_val = raw_measured[1].replace('\n', ' ')
            else:
                measured_unit = ''
                measured_val = ''
                
            # Extract uncertainty
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
            
            # Store additional info in calibration_info
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
        
        # Prepare data for XML
        # Core data
        software_name = "DigiCert"
        software_release = "v0.0"
        country_code_iso = "PH"
        used_lang_code = "en"
        mandatory_lang_code = "en"
        unique_identifier = "Calibration No. " + calibration_info["certificate_number"]
        raw_date = calibration_info.get("calibration_date", "")
        step1 = re.sub(r"([A-Za-z]+)(\d)", r"\1 \2", raw_date)
        step2 = step1.replace(",", ", ")
        norm = re.sub(r"\s+", " ", step2).strip()
        try:
            dt = datetime.strptime(norm, "%B %d, %Y")
            begin_performance_date = dt.strftime("%Y-%m-%d")
        except ValueError:
            begin_performance_date = ""
        end_performance_date = ""
        performance_location = "LABORATORY"
        
        # Items
        item_name = calibration_info.get("calibration_item", "")
        item_model = calibration_info["make_model"]
        id_issuer = "customer"
        id_name = calibration_info["calibration_item"]
        id_serialnum = calibration_info["serial_number"]
        capacity = "Capacity: " + calibration_info["capacity"]
        measurement_range = "Measurement Range: " + calibration_info["measurement_range"]
        resolution = "Resolution: " + calibration_info["resolution"]
        standard_name = calibration_info["standard_item"]
        standard_model = calibration_info["standard_model"]
        standard_id_issuer = "LABORATORY"
        standard_id_name = calibration_info["standard_item"]
        standard_id_serialnum = calibration_info["standard_serial_number"]
        standard_certificate_number = "Calibration Certificate No.: " + calibration_info["standard_cert_number"]
        standard_traceability = "Traceability: " + calibration_info["standard_traceability"]
        
        # Calibration lab
        calibration_labcode = "FORC"
        calibration_contactname = "National Metrology Laboratory - Industrial Technology Development Institute"
        calibration_labcity = "Taguig"
        calibration_labcountrycode = "PH"
        calibration_lab_postcode = "1633"
        calibration_labstreet = "General Santos Ave"
        
        # Responsible persons
        if "resp_person1_name" in calibration_info and "resp_person1_role" in calibration_info:
            resp1_name = calibration_info["resp_person1_name"]
            resp1_role = calibration_info["resp_person1_role"]
        else:
            resp1_name = ""
            resp1_role = ""

        if "resp_person2_name" in calibration_info and "resp_person2_role" in calibration_info:
            resp2_name = calibration_info["resp_person2_name"]
            resp2_role = calibration_info["resp_person2_role"]
        else:
            resp2_name = ""
            resp2_role = ""

        if "resp_person3_name" in calibration_info and "resp_person3_role" in calibration_info:
            resp3_name = calibration_info["resp_person3_name"]
            resp3_role = calibration_info["resp_person3_role"]
        else:
            resp3_name = ""
            resp3_role = ""
        
        # Customer
        customer_name = calibration_info["customer_name"]
        customer_address = calibration_info.get("customer_address", "")
        
        # Measurement results
        measurement_item = calibration_info["calibration_item"]
        measurement_method = calibration_info["relative_uncertainty"]
        measurement_desc = calibration_info["uncertainty_of_measurement"]
        influencecondition1 = "Ambient Temperature"
        temperature = calibration_info["temperature"]
        unit1 = "°C"
        influencecondition2 = "Relative Humidity"
        humidity = calibration_info["humidity"]
        unit2 = "%"
        measurement_standard = calibration_info["standard_measurement"]
        measurement_standard_values = calibration_info["standard_measurement_values"]
        measurement_standard_unit = ' '.join([f'\\{calibration_info["standard_measurement_unit"]}'] * value_count)
        measured_item = calibration_info["measured_item"]
        measured_item_values = calibration_info["measured_item_values"]
        measured_item_unit = ' '.join([f'\\{calibration_info["measured_item_unit"]}'] * value_count)
        measurement_error = calibration_info["relative_uncertainty"]
        measurement_error_values = calibration_info["relative_uncertainty_values"]
        measurement_error_unit = ' '.join([f'\\{calibration_info["relative_uncertainty_unit"]}'] * value_count)
        calibrationprocedure = "CALIBRATION PROCEDURE: " + calibration_info["calibration_procedure"]
        remarks = "REMARKS: " + calibration_info["remarks"]
        
        # Parse template, register namespaces
        ns = {"dcc":"https://ptb.de/dcc","si":"https://ptb.de/si"}
        for p,u in ns.items(): ET.register_namespace(p,u)
        
        from xml.etree.ElementTree import ParseError
        try:
            tree = ET.parse(template)
        except ParseError as e:
            # fallback to lxml recovery if available
            try:
                from lxml import etree as LET
                parser = LET.XMLParser(recover=True)
                tree = LET.parse(template, parser)
            except ImportError:
                raise e
                
        root = tree.getroot()
        
        def set_text(elem, txt, lang=None):
            if elem is None or txt is None: return
            elem.text = txt
            if lang: elem.set("lang", lang)
            
        # 1) software
        sw = root.find(".//dcc:software", ns)
        set_text(sw.find("dcc:name/dcc:content", ns), software_name)
        set_text(sw.find("dcc:release", ns), software_release)

        # 2) coreData
        cd = root.find(".//dcc:coreData", ns)
        set_text(cd.find("dcc:countryCodeISO3166_1", ns), country_code_iso)
        set_text(cd.find("dcc:usedLangCodeISO639_1", ns), used_lang_code)
        set_text(cd.find("dcc:mandatoryLangCodeISO639_1", ns), mandatory_lang_code)
        set_text(cd.find("dcc:uniqueIdentifier", ns), unique_identifier)
        set_text(cd.find("dcc:beginPerformanceDate", ns), begin_performance_date)
        set_text(cd.find("dcc:endPerformanceDate", ns), end_performance_date)
        set_text(cd.find("dcc:performanceLocation", ns), performance_location)

        # 3) items: first is calibration, second is standard
        items = root.findall(".//dcc:items/dcc:item", ns)

        # calibration item
        if items:
            ci = items[0]
            set_text(ci.find("dcc:name/dcc:content", ns), item_name, lang=used_lang_code)
            set_text(ci.find("dcc:manufacturer/dcc:name/dcc:content", ns), "", lang=used_lang_code)
            set_text(ci.find("dcc:model", ns), item_model)
            ident = ci.find("dcc:identifications/dcc:identification", ns)
            if ident is not None:
                set_text(ident.find("dcc:issuer", ns), id_issuer)
                set_text(ident.find("dcc:value", ns), id_name)
                set_text(ident.find("dcc:name/dcc:content", ns), id_serialnum, lang=used_lang_code)
            desc = ci.find("dcc:description", ns)
            if desc is not None:
                cont = desc.findall("dcc:content", ns)
                if len(cont)>0: set_text(cont[0], capacity, lang=used_lang_code)
                if len(cont)>1: set_text(cont[1], measurement_range, lang=used_lang_code)
                if len(cont)>2: set_text(cont[2], resolution, lang=used_lang_code)

        # standard item
        if len(items)>1:
            si_el = items[1]
            set_text(si_el.find("dcc:name/dcc:content", ns), standard_name, lang=used_lang_code)
            set_text(si_el.find("dcc:manufacturer/dcc:name/dcc:content", ns), "", lang=used_lang_code)
            set_text(si_el.find("dcc:model", ns), standard_model)
            ident2 = si_el.find("dcc:identifications/dcc:identification", ns)
            if ident2 is not None:
                set_text(ident2.find("dcc:issuer", ns), standard_id_issuer)
                set_text(ident2.find("dcc:value", ns), standard_id_serialnum)
                set_text(ident2.find("dcc:name/dcc:content", ns), standard_id_name, lang=used_lang_code)
            desc2 = si_el.find("dcc:description", ns)
            if desc2 is not None:
                cont2 = desc2.findall("dcc:content", ns)
                if len(cont2)>0: set_text(cont2[0], standard_certificate_number, lang=used_lang_code)
                if len(cont2)>1: set_text(cont2[1], standard_traceability, lang=used_lang_code)

        # 4) calibrationLaboratory
        lab = root.find(".//dcc:calibrationLaboratory", ns)
        set_text(lab.find("dcc:calibrationLaboratoryCode", ns), calibration_labcode)
        set_text(lab.find("dcc:contact/dcc:name/dcc:content", ns), calibration_contactname, lang=used_lang_code)
        loc = lab.find("dcc:contact/dcc:location", ns)
        set_text(loc.find("dcc:city", ns), calibration_labcity)
        set_text(loc.find("dcc:countryCode", ns), calibration_labcountrycode)
        set_text(loc.find("dcc:postCode", ns), calibration_lab_postcode)
        set_text(loc.find("dcc:street", ns), calibration_labstreet)

        # 5) respPersons
        resp_nodes = root.findall(".//dcc:respPersons/dcc:respPerson", ns)
        for idx,(name,role) in enumerate([(resp1_name,resp1_role),(resp2_name,resp2_role),(resp3_name,resp3_role)]):
            if idx<len(resp_nodes):
                rp = resp_nodes[idx]
                set_text(rp.find("dcc:person/dcc:name/dcc:content", ns), name, lang=used_lang_code)
                set_text(rp.find("dcc:role", ns), role)

        # 6) customer
        cust = root.find(".//dcc:customer", ns)
        set_text(cust.find("dcc:name/dcc:content", ns), customer_name)
        f = cust.find("dcc:location/dcc:further/dcc:content", ns)
        set_text(f, customer_address, lang=used_lang_code)

        # 7) measurementResults
        mr = root.find(".//dcc:measurementResults", ns)
        set_text(mr.find("dcc:name/dcc:content", ns), measurement_item, lang=used_lang_code)
        um = mr.find("dcc:usedMethods/dcc:usedMethod", ns)
        set_text(um.find("dcc:name/dcc:content", ns), measurement_method, lang=used_lang_code)
        set_text(um.find("dcc:description/dcc:content", ns), measurement_desc, lang=used_lang_code)

        # 7) influenceConditions
        ic = mr.find(".//dcc:influenceConditions", ns)
        if ic is None:
            print("⚠️ influenceConditions not found")
        else:
            conds = ic.findall("dcc:influenceCondition", ns)
            # first condition
            if len(conds) > 0:
                infl = conds[0]
                set_text(infl.find("dcc:name/dcc:content", ns), influencecondition1, lang=used_lang_code)
                dq = infl.find(".//dcc:quantity", ns)
                set_text(dq.find("dcc:name/dcc:content", ns), influencecondition1, lang=used_lang_code)
                real = dq.find("si:real", ns)
                set_text(real.find("si:value", ns), temperature)
                set_text(real.find("si:unit", ns), "\\" + unit1)
            # second condition
            if len(conds) > 1:
                infl = conds[1]
                set_text(infl.find("dcc:name/dcc:content", ns), influencecondition2, lang=used_lang_code)
                dq = infl.find(".//dcc:quantity", ns)
                set_text(dq.find("dcc:name/dcc:content", ns), influencecondition2, lang=used_lang_code)
                real = dq.find("si:real", ns)
                set_text(real.find("si:value", ns), humidity)
                set_text(real.find("si:unit", ns), "\\" + unit2)

        # 8) results
        res = mr.find(".//dcc:results", ns)
        if res is None:
            print("⚠️ results not found")
        else:
            # define your three rows in lists
            names = [measurement_standard, measured_item, measurement_error]
            values = [measurement_standard_values, measured_item_values, measurement_error_values]
            units = [measurement_standard_unit, measured_item_unit, measurement_error_unit]
            for idx, row in enumerate(res.findall("dcc:result", ns)):
                # name
                set_text(row.find("dcc:name/dcc:content", ns), names[idx], lang=used_lang_code)
                # realListXMLList
                real_list = row.find(".//si:realListXMLList", ns)
                if real_list is not None:
                    set_text(real_list.find("si:valueXMLList", ns), values[idx])
                    set_text(real_list.find("si:unitXMLList", ns), units[idx])

        # 8) comment
        comm = root.find(".//dcc:comment", ns)
        cc = comm.findall("dcc:content", ns)
        if cc: 
            set_text(cc[0], calibrationprocedure, lang=used_lang_code)
        if len(cc)>1: 
            set_text(cc[1], remarks, lang=used_lang_code)


        # Fix 1: Use os.path.join (recommended)
        output = os.path.join("valid xml", unique_identifier + "_DCC.xml")
        # write
        tree.write(output, encoding="utf-8", xml_declaration=True)
        
        messagebox.showinfo("Success", f"XML file created successfully at: {output}")
        return output
        
      
    
   


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