import re
import subprocess
from tkinter import messagebox
from xml.etree.ElementTree import ParseError
from customtkinter import *
from PIL import Image
import os
from PIL import Image
import json
import xml.etree.ElementTree as ET
import lxml.etree as LET
from io import BytesIO
from tkinter import filedialog   # you’ll need this up top if you also do file‐saves later


#import static_info.json
# Load the JSON data from the file using absolute path
def run_app(script_dir, config_path):
    
    # script_dir = os.path.dirname(os.path.abspath(__file__))
    # config_path = os.path.join(script_dir, 'static_info.json')
    try:
        with open(config_path, 'r') as file:
            cfg = json.load(file)
    except FileNotFoundError:
        print(f"Error: Could not find the configuration file at: {config_path}")
        print("Current working directory:", os.getcwd())
        print("Looking for file in directory:", script_dir)
        raise


    def back_to_menu():
        app.destroy()  # Close the current app window
        import index
        index.run_app()
        # subprocess.Popen(["python",  os.path.join(os.path.dirname(__file__),"index.py")])


    def center_window(app, width, height):
        app.update_idletasks()  # Ensure the window dimensions are updated
        screen_width = app.winfo_screenwidth()
        screen_height = app.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        app.geometry(f"{width}x{height}+{x}+{y}")

    app = CTk()
    app.title("DigiCert")
    app_width = 1200
    app_height = 700
    center_window(app, app_width, app_height)  # Call the function to center the window
    set_appearance_mode("light")

    # Disable maximize button
    app.resizable(False, False)

    # Create a CTkFrame to act as the background (canvas)
    bg_frame = CTkFrame(master=app, fg_color="white") 
    bg_frame.place(relx=0, rely=0, relwidth=1, relheight=1)  

    # Compute relx and rely based on 58x84 starting point in a 1200x700 canvas
    relx = 58 / 1200 
    rely = 84 / 700 
    relwidth = 475 / 1200  
    relheight = 525 / 700  

    # Debounce logic for preview update
    preview_update_job = [None]  # Mutable container for job id

    def debounce_update_preview(widget):
        if preview_update_job[0]:
            app.after_cancel(preview_update_job[0])
        preview_update_job[0] = app.after(250, lambda: update_preview(widget))

    # Create a scrollable frame
    scrollable_frame = CTkScrollableFrame(master=app, fg_color='white')
    scrollable_frame.place(relx=relx, rely=rely, relwidth=relwidth, relheight=relheight)

    ###############################
    # Title inside scrollable frame
    titleLabel = CTkLabel(master=scrollable_frame, text="Request Details:", font=("Inter", 14, "bold"), bg_color='white')
    titleLabel.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

    # TSR Number Label
    tsr_label = CTkLabel(master=scrollable_frame, text="TSR Number:", font=("Inter", 12, "bold"), bg_color='white')
    tsr_label.grid(row=1, column=0, padx=10, pady=(5, 5), sticky="w")

    # TSR Number Textbox
    tsr_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. 02-2019-FORC-0028")
    tsr_textbox.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="w")

    # Calibration Type Label
    calibration_label = CTkLabel(master=scrollable_frame, text="Calibration Type:", font=("Inter", 12, "bold"), bg_color='white')
    calibration_label.grid(row=1, column=1, padx=10, pady=(5, 5), sticky="w")

    # Calibration Type Dropdown
    calibration_options = ["Onsite", "Laboratory"]  # Replace with your actual options
    calibration_dropdown = CTkOptionMenu(
        master=scrollable_frame,
        values=calibration_options,
        font=("Inter", 12),
        width=170,
        height=30,
        fg_color='white',
        text_color='black',
    )
    calibration_dropdown.grid(row=2, column=1, padx=10, pady=(5, 10), sticky="w")

    # Start Date of Calibration Label
    start_date_label = CTkLabel(master=scrollable_frame, text="Start Date of Calibration:", font=("Inter", 12, "bold"), bg_color='white')
    start_date_label.grid(row=3, column=0, padx=10, pady=(5, 5), sticky="w")

    # Start Date of Calibration Textbox
    start_date_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. 2025-02-24")
    start_date_textbox.grid(row=4, column=0, padx=10, pady=(5, 10), sticky="w")

    # End Date of Calibration Label
    end_date_label = CTkLabel(master=scrollable_frame, text="End Date of Calibration:", font=("Inter", 12, "bold"), bg_color='white')
    end_date_label.grid(row=3, column=1, padx=10, pady=(5, 5), sticky="w")

    # End Date of Calibration Textbox
    end_date_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. 2025-02-24")
    end_date_textbox.grid(row=4, column=1, padx=10, pady=(5, 10), sticky="w")

    #############################
    # Calibration Equipment Label
    calibration_equipment_label = CTkLabel(master=scrollable_frame, text="Calibration Equipment:", font=("Inter", 14, "bold"), bg_color='white')
    calibration_equipment_label.grid(row=7, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

    # Calibration Item Label
    calibration_item_label = CTkLabel(master=scrollable_frame, text="Calibration Item:", font=("Inter", 12, "bold"), bg_color='white')
    calibration_item_label.grid(row=8, column=0, padx=10, pady=(5, 5), sticky="w")

    # Calibration Item Dropdown
    calibration_item_options = [
        "Box Compression Machine", 
        "Axle Weighing Scale", 
        "Universal Testing Machine", 
        "Edge Crush Testing Machine", 
        "Ring Crush Testing Machine", 
        "Compression Testing Machine", 
        "Tensile Testing Machine", 
        "Force Measuring Instrument"
    ]

    calibration_item_dropdown = CTkOptionMenu(
        master=scrollable_frame,
        values=calibration_item_options,
        font=("Inter", 12),
        width=200,
        height=30,
        fg_color='white',
        text_color='black',
    )
    calibration_item_dropdown.grid(row=9, column=0, padx=10, pady=(5, 10), sticky="w")


    # Serial Number Label
    serial_number_label = CTkLabel(master=scrollable_frame, text="Serial Number:", font=("Inter", 12, "bold"), bg_color='white')
    serial_number_label.grid(row=8, column=1, padx=10, pady=(5, 5), sticky="w")

    # Serial Number Textbox
    serial_number_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. 1122YL23002")
    serial_number_textbox.grid(row=9, column=1, padx=10, pady=(5, 10), sticky="w")


    # Capacity Label
    capacity_label = CTkLabel(master=scrollable_frame, text="Capacity:", font=("Inter", 12, "bold"), bg_color='white')
    capacity_label.grid(row=10, column=1, padx=10, pady=(5, 5), sticky="w")

    # Capacity Textbox
    capacity_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. 1000 kgf")
    capacity_textbox.grid(row=11, column=1, padx=10, pady=(5, 10), sticky="w")

    # Model Label
    model_label = CTkLabel(master=scrollable_frame, text="Model:", font=("Inter", 12, "bold"), bg_color='white')
    model_label.grid(row=12, column=0, padx=10, pady=(5, 5), sticky="w")

    # Model Textbox
    model_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. Intercomp")
    model_textbox.grid(row=13, column=0, padx=10, pady=(5, 10), sticky="w")

    # Range Label
    range_label = CTkLabel(master=scrollable_frame, text="Range:", font=("Inter", 12, "bold"), bg_color='white')
    range_label.grid(row=12, column=1, padx=10, pady=(5, 5), sticky="w")

    # Range Textbox
    range_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. 0 kgf to 15 000 kgf")
    range_textbox.grid(row=13, column=1, padx=10, pady=(5, 10), sticky="w")

    # Identification Issuer Label
    identification_issuer_label = CTkLabel(master=scrollable_frame, text="Identification Issuer:", font=("Inter", 12, "bold"), bg_color='white')
    identification_issuer_label.grid(row=10, column=0, padx=10, pady=(5, 5), sticky="w")

    # Identification Issuer Textbox
    identification_issuer_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. customer")
    identification_issuer_textbox.grid(row=11, column=0, padx=10, pady=(5, 10), sticky="w")

    # Resolution Label
    resolution_label = CTkLabel(master=scrollable_frame, text="Resolution:", font=("Inter", 12, "bold"), bg_color='white')
    resolution_label.grid(row=14, column=0, padx=10, pady=(5, 5), sticky="w")

    # Resolution Textbox
    resolution_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. 50 kgf")
    resolution_textbox.grid(row=15, column=0, padx=10, pady=(5, 10), sticky="w")

    ##########################
    # Standard Equipment Label
    standard_equipment_label = CTkLabel(master=scrollable_frame, text="Standard Equipment:", font=("Inter", 14, "bold"), bg_color='white')
    standard_equipment_label.grid(row=16, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

    # Standard Item Label
    standard_item_label1 = CTkLabel(master=scrollable_frame, text="Standard Item:", font=("Inter", 12, "bold"), bg_color='white')
    standard_item_label1.grid(row=17, column=0, padx=10, pady=(5, 5), sticky="w")

    # Standard Item Textbox
    standard_item_textbox1 = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. Force Measuring Equipment")
    standard_item_textbox1.grid(row=18, column=0, padx=10, pady=(5, 10), sticky="w")

    # Serial Number Label
    serial_number_label1 = CTkLabel(master=scrollable_frame, text="Serial Number:", font=("Inter", 12, "bold"), bg_color='white')
    serial_number_label1.grid(row=17, column=1, padx=10, pady=(5, 5), sticky="w")

    # Serial Number Textbox
    serial_number_textbox1 = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. SN 1251056K0094")
    serial_number_textbox1.grid(row=18, column=1, padx=10, pady=(5, 10), sticky="w")


    # Calibration Cert Label
    calibCert_label = CTkLabel(master=scrollable_frame, text="Calibration Certificate No.", font=("Inter", 12, "bold"), bg_color='white')
    calibCert_label.grid(row=19, column=1, padx=10, pady=(5, 5), sticky="w")

    # Calibration Cert Textbox
    calibCert_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. 11-2020-FORC-0116")
    calibCert_textbox.grid(row=20, column=1, padx=10, pady=(5, 10), sticky="w")

    # Model Label
    model_label1 = CTkLabel(master=scrollable_frame, text="Model:", font=("Inter", 12, "bold"), bg_color='white')
    model_label1.grid(row=21, column=0, padx=10, pady=(5, 5), sticky="w")

    # Model Textbox
    model_textbox1 = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. Shimadzu/ UH-F1000kNX")
    model_textbox1.grid(row=22, column=0, padx=10, pady=(5, 10), sticky="w")

    # Traceability Label
    traceability_label = CTkLabel(master=scrollable_frame, text="Traceability:", font=("Inter", 12, "bold"), bg_color='white')
    traceability_label.grid(row=21, column=1, padx=10, pady=(5, 5), sticky="w")

    # Traceability Textbox
    traceability_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. Traceable to the SI through NMD-ITDI")
    traceability_textbox.grid(row=22, column=1, padx=10, pady=(5, 10), sticky="w")

    # Identification Issuer Label
    identification_issuer_label1 = CTkLabel(master=scrollable_frame, text="Identification Issuer:", font=("Inter", 12, "bold"), bg_color='white')
    identification_issuer_label1.grid(row=19, column=0, padx=10, pady=(5, 5), sticky="w")

    # Identification Issuer Textbox
    identification_issuer_textbox1 = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. laboratory")
    identification_issuer_textbox1.grid(row=20, column=0, padx=10, pady=(5, 10), sticky="w")

    #################
    # Personnel Label
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
    temperature_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. (22 +- 2)")
    temperature_textbox.grid(row=37, column=0, padx=10, pady=(5, 10), sticky="w")

    # Unit Label (Temperature)
    temperature_unit_label = CTkLabel(master=scrollable_frame, text="Unit:", font=("Inter", 12, "bold"), bg_color='white')
    temperature_unit_label.grid(row=36, column=1, padx=10, pady=(5, 5), sticky="w")

    # Unit Textbox (Temperature)
    temperature_unit_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. celcius")
    temperature_unit_textbox.grid(row=37, column=1, padx=10, pady=(5, 10), sticky="w")

    # Humidity Label
    humidity_label = CTkLabel(master=scrollable_frame, text="Humidity:", font=("Inter", 12, "bold"), bg_color='white')
    humidity_label.grid(row=38, column=0, padx=10, pady=(5, 5), sticky="w")

    # Humidity Textbox
    humidity_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. (40 +- 5)")
    humidity_textbox.grid(row=39, column=0, padx=10, pady=(5, 10), sticky="w")

    # Unit Label (Humidity)
    humidity_unit_label = CTkLabel(master=scrollable_frame, text="Unit:", font=("Inter", 12, "bold"), bg_color='white')
    humidity_unit_label.grid(row=38, column=1, padx=10, pady=(5, 5), sticky="w")

    # Unit Textbox (Humidity)
    humidity_unit_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. %")
    humidity_unit_textbox.grid(row=39, column=1, padx=10, pady=(5, 10), sticky="w")

    ##########################
    results_label = CTkLabel(master=scrollable_frame, text="Results:", font=("Inter", 14, "bold"), bg_color='white')
    results_label.grid(row=40, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")
    # Standard Measurement Label
    standard_measurement_label = CTkLabel(master=scrollable_frame, text="Standard Measurement:", font=("Inter", 12, "bold"), bg_color='white')
    standard_measurement_label.grid(row=41, column=0, padx=10, pady=(5, 5), sticky="w")

    # Standard Measurement Textbox
    standard_measurement_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. 0.00 3 000 6 000")
    standard_measurement_textbox.grid(row=42, column=0, padx=10, pady=(5, 10), sticky="w")

    # Unit Label (Standard Measurement)
    standard_measurement_unit_label = CTkLabel(master=scrollable_frame, text="Unit:", font=("Inter", 12, "bold"), bg_color='white')
    standard_measurement_unit_label.grid(row=41, column=1, padx=10, pady=(5, 5), sticky="w")

    # Unit Textbox (Standard Measurement)
    standard_measurement_unit_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. \kgf \kgf \kgf")
    standard_measurement_unit_textbox.grid(row=42, column=1, padx=10, pady=(5, 10), sticky="w")


    # Indicated Measurement Label
    indicated_measurement_label = CTkLabel(master=scrollable_frame, text="Indicated Measurement:", font=("Inter", 12, "bold"), bg_color='white')
    indicated_measurement_label.grid(row=43, column=0, padx=10, pady=(5, 5), sticky="w")

    # Indicated Measurement Textbox
    indicated_measurement_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. 0.00 2 850 5 700")
    indicated_measurement_textbox.grid(row=44, column=0, padx=10, pady=(5, 10), sticky="w")


    # Unit Label (Indicated Measurement)
    indicated_measurement_unit_label = CTkLabel(master=scrollable_frame, text="Unit:", font=("Inter", 12, "bold"), bg_color='white')
    indicated_measurement_unit_label.grid(row=43, column=1, padx=10, pady=(5, 5), sticky="w")

    # Unit Textbox (Indicated Measurement)
    indicated_measurement_unit_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. \kgf \kgf \kgf")
    indicated_measurement_unit_textbox.grid(row=44, column=1, padx=10, pady=(5, 10), sticky="w")


    # Measurement Error Label
    measurement_error_label = CTkLabel(master=scrollable_frame, text="Measurement Error:", font=("Inter", 12, "bold"), bg_color='white')
    measurement_error_label.grid(row=45, column=0, padx=10, pady=(5, 5), sticky="w")

    # Measurement Error Textbox
    measurement_error_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. 0.00 1.04 0.56")
    measurement_error_textbox.grid(row=46, column=0, padx=10, pady=(5, 10), sticky="w")


    # Unit Label (Measurement Error)
    measurement_error_unit_label = CTkLabel(master=scrollable_frame, text="Unit:", font=("Inter", 12, "bold"), bg_color='white')
    measurement_error_unit_label.grid(row=45, column=1, padx=10, pady=(5, 5), sticky="w")

    # Unit Textbox (Measurement Error)
    measurement_error_unit_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. \% \% \%")
    measurement_error_unit_textbox.grid(row=46, column=1, padx=10, pady=(5, 10), sticky="w")

    # Relative Expanded Uncertainty Label
    relative_expanded_uncertainty_label = CTkLabel(master=scrollable_frame, text="Relative Expanded Uncertainty:", font=("Inter", 12, "bold"), bg_color='white')
    relative_expanded_uncertainty_label.grid(row=47, column=0, padx=10, pady=(5, 5), sticky="w")

    # Relative Expanded Uncertainty Textbox
    relative_expanded_uncertainty_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. 0.00 1.04 0.56")
    relative_expanded_uncertainty_textbox.grid(row=48, column=0, padx=10, pady=(5, 10), sticky="w")


    # Unit Label (Relative Expanded Uncertainty)
    relative_expanded_uncertainty_unit_label = CTkLabel(master=scrollable_frame, text="Unit:", font=("Inter", 12, "bold"), bg_color='white')
    relative_expanded_uncertainty_unit_label.grid(row=47, column=1, padx=10, pady=(5, 5), sticky="w")

    # Unit Textbox (Relative Expanded Uncertainty)
    relative_expanded_uncertainty_unit_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. \% \% \%")
    relative_expanded_uncertainty_unit_textbox.grid(row=48, column=1, padx=10, pady=(5, 10), sticky="w")

    # Repeatability Error Label
    repeatability_error_label = CTkLabel(master=scrollable_frame, text="Repeatability Error:", font=("Inter", 12, "bold"), bg_color='white')
    repeatability_error_label.grid(row=49, column=0, padx=10, pady=(5, 5), sticky="w")

    # Repeatability Error Textbox
    repeatability_error_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. 0.00 0.50 0.30")
    repeatability_error_textbox.grid(row=50, column=0, padx=10, pady=(5, 10), sticky="w")

    # Unit Label (Repeatability Error)
    repeatability_error_unit_label = CTkLabel(master=scrollable_frame, text="Unit:", font=("Inter", 12, "bold"), bg_color='white')
    repeatability_error_unit_label.grid(row=49, column=1, padx=10, pady=(5, 5), sticky="w")

    # Unit Textbox (Repeatability Error)
    repeatability_error_unit_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. \% \% \%")
    repeatability_error_unit_textbox.grid(row=50, column=1, padx=10, pady=(5, 10), sticky="w")



    #############################
    # Uncertainty of Measurement Label
    uncertainty_label = CTkLabel(master=scrollable_frame, text="Uncertainty of Measurement:", font=("Inter", 14, "bold"), bg_color='white')
    uncertainty_label.grid(row=51, column=0, padx=10, pady=(5, 5), sticky="w")

    # Define placeholder text and color
    uncertainty_placeholder = "e.g. The uncertainty stated is the expanded uncertainty obtained by multiplying the standard uncertainty..."

    def on_uncertainty_focus_in(event):
        current_text = uncertainty_textbox.get("1.0", "end-1c")
        if current_text == uncertainty_placeholder:
            uncertainty_textbox.delete("1.0", "end")
            uncertainty_textbox.configure(text_color="black")

    def on_uncertainty_focus_out(event):
        current_text = uncertainty_textbox.get("1.0", "end-1c").strip()
        if current_text == "":
            uncertainty_textbox.insert("1.0", uncertainty_placeholder)
            uncertainty_textbox.configure(text_color="gray")

    # Uncertainty of Measurement Textbox (Multiline with wrapping)
    uncertainty_textbox = CTkTextbox(
        master=scrollable_frame,
        font=("Inter", 12),
        fg_color='white',
        text_color="gray",
        border_width=2,
        height=90,
        wrap='word'
    )
    uncertainty_textbox.insert("1.0", uncertainty_placeholder)
    uncertainty_textbox.bind("<FocusIn>", on_uncertainty_focus_in)
    uncertainty_textbox.bind("<FocusOut>", on_uncertainty_focus_out)
    uncertainty_textbox.grid(row=52, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="we")
    uncertainty_textbox.delete("1.0", "end")
    uncertainty_textbox.configure(text_color="black")

    #############################
    # Calibration Procedure Label
    calibration_procedure_label = CTkLabel(master=scrollable_frame, text="Calibration Procedure:", font=("Inter", 14, "bold"), bg_color='white')
    calibration_procedure_label.grid(row=53, column=0, padx=10, pady=(5, 5), sticky="w")

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
    calibration_procedure_textbox.grid(row=54, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="we")
    calibration_procedure_textbox.delete("1.0", "end")
    calibration_procedure_textbox.configure(text_color="black")

    ###############
    # Remarks Label
    remarks_label = CTkLabel(master=scrollable_frame, text="Remarks:", font=("Inter", 14, "bold"), bg_color='white')
    remarks_label.grid(row=55, column=0, padx=10, pady=(5, 5), sticky="w")

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
    remarks_textbox.grid(row=56, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="we")
    remarks_textbox.delete("1.0", "end")
    remarks_textbox.configure(text_color="black")



    # ^ content of scrollable frame
    #########################################

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

    # Export button
    exportButton = CTkButton(master=app, text="Export", corner_radius=7, 
                            fg_color="#010E54", hover_color="#1A4F8B", font=("Inter", 13))
    exportButton.place(relx=0.1958, rely=0.9214, relwidth=0.1008, relheight=0.0471)

    # Back button
    backButton = CTkButton(master=app, text="< ", corner_radius=7, 
                        fg_color="#010E54", hover_color="#1A4F8B", font=("Inter", 15),
                        command=back_to_menu)
    backButton.place(relx=0.0225, rely=0.0486, relwidth=0.0200, relheight=0.0350)
    # PDF to XML label
    titleLabel = CTkLabel(master=app, text="New XML", font=("Inter", 13, "bold"), bg_color='white')
    titleLabel.place(relx=0.1800, rely=0.0514)


    def highlight_empty_fields():
        for w in scrollable_frame.winfo_children():
            # CTkEntry → use its internal _entry widget
            if isinstance(w, CTkEntry):
                def on_done(e, widget=w):
                    ok = widget.get().strip()
                    widget.configure(border_color="green" if ok else "red")
                w._entry.bind("<FocusOut>", on_done)
                on_done(None)  # set initial color

            # CTkTextbox → use its internal _textbox widget
            elif isinstance(w, CTkTextbox):
                def on_done_txt(e, widget=w):
                    txt = widget.get("1.0","end-1c").strip()
                    is_ph = txt in (
                        placeholder_text.strip(),
                        remarks_placeholder.strip(),
                        uncertainty_placeholder.strip()
                    )
                    widget.configure(border_color="green" if txt and not is_ph else "red")
                w._textbox.bind("<FocusOut>", on_done_txt)
                on_done_txt(None)  # initial color

    # call once after building all widgets
    highlight_empty_fields()

    # 1) Collect every field in collect_calibration_info()
    def collect_calibration_info():
        calibration_info = {
            # static JSON:
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
            # core data
            "certificate_number": "Calibration No. " + tsr_textbox.get(),
            "calibration_date": start_date_textbox.get(),
            "calibration_enddate": start_date_textbox.get(),
            "calibration_location": calibration_dropdown.get(),
            # items
            "calibration_item": calibration_item_dropdown.get(),
            "make_model": model_textbox.get(),
            "serial_number": serial_number_textbox.get(),
            "capacity": "Capacity: " + capacity_textbox.get(),
            "measurement_range": "Measurement Range: " + range_textbox.get(),
            "resolution": "Resolution: " + resolution_textbox.get(),
            "identification_issuer": identification_issuer_textbox.get(),
            
            # standard
            "standard_item": standard_item_textbox1.get(),
            "standard_model": model_textbox1.get(),
            "standard_serial_number": serial_number_textbox1.get(),
            "standard_cert_number": "Calibration Certificate No.: " + calibCert_textbox.get(),
            "standard_traceability": "Traceability: " + traceability_textbox.get(),
            
            "standard_item_issuer": identification_issuer_textbox1.get(),
            # persons
            "resp_person1_name": analyst1_textbox.get(),
            "resp_person1_role": role1_textbox.get(),
            "resp_person2_name": analyst2_textbox.get(),
            "resp_person2_role": role2_textbox.get(),
            "resp_person3_name": authorized_textbox.get(),
            "resp_person3_role": authorized_role_textbox.get(),
            # customer
            "customer_name": customer_textbox.get(),
            "customer_address": address_textbox.get(),
            # conditions/results
            "temperature": temperature_textbox.get(),
            "temperature_unit": temperature_unit_textbox.get(),
            "humidity": humidity_textbox.get(),
            "humidity_unit": humidity_unit_textbox.get(),
            "standard_measurement_values": standard_measurement_textbox.get(),
            "standard_measurement_unit": standard_measurement_unit_textbox.get(),
            "measurement_standard": "Standard Measurement",
            "measured_item": "Indicated Measurement",
            "measured_item_values": indicated_measurement_textbox.get(),
            "measured_item_unit": indicated_measurement_unit_textbox.get(),
            "relative_uncertainty_values": relative_expanded_uncertainty_textbox.get(),
            "relative_uncertainty_unit": relative_expanded_uncertainty_unit_textbox.get(),
            "relative_uncertainty": "Relative Expanded Uncertainty",
            "measurement_error_values": measurement_error_textbox.get(),
            "measurement_error_unit": measurement_error_unit_textbox.get(),
            "measurement_error": "Measurement Error",
            "repeatability_error_values": repeatability_error_textbox.get(),
            "repeatability_error_unit": repeatability_error_unit_textbox.get(),
            "repeatability_error": "Repeatability Error",
            # big text areas
            "calibration_procedure": calibration_procedure_textbox.get("1.0", "end-1c").replace(placeholder_text, ""),
            "remarks": remarks_textbox.get("1.0", "end-1c").replace(remarks_placeholder, ""),
            "uncertainty_of_measurement": uncertainty_textbox.get("1.0", "end-1c").replace(uncertainty_placeholder, "")

        }
        return calibration_info


    def generate_xml_tree(info):
        template = os.path.join(script_dir, "template.xml")
        for p,u in {"dcc":"https://ptb.de/dcc","si":"https://ptb.de/si"}.items():
            ET.register_namespace(p,u)

        try:
            tree = ET.parse(template)
        except ParseError:
            parser = LET.XMLParser(recover=True)
            tree = LET.parse(template, parser)
        root = tree.getroot()

        def set_text(elem, txt, lang=None):
            if elem is None or txt is None: return
            elem.text = txt
            if lang: elem.set("lang", lang)

        ns = {"dcc":"https://ptb.de/dcc","si":"https://ptb.de/si"}

        # 1) software
        sw = root.find(".//dcc:software", ns)
        set_text(sw.find("dcc:name/dcc:content", ns), info["software_name"])
        set_text(sw.find("dcc:release", ns), info["software_release"])

        # 2) coreData
        cd = root.find(".//dcc:coreData", ns)
        set_text(cd.find("dcc:uniqueIdentifier", ns), info["certificate_number"])
        set_text(cd.find("dcc:beginPerformanceDate", ns), info["calibration_date"])
        set_text(cd.find("dcc:endPerformanceDate", ns), info["calibration_enddate"])
        set_text(cd.find("dcc:performanceLocation", ns), info["calibration_location"])

        # 3) first item (your device)
        items = root.findall(".//dcc:items/dcc:item", ns)
        if items:
            ci = items[0]
            set_text(ci.find("dcc:name/dcc:content", ns), info["calibration_item"], lang=info["used_lang_code"])
            set_text(ci.find("dcc:model", ns), info["make_model"])
            ident = ci.find("dcc:identifications/dcc:identification", ns)
            if ident is not None:
                set_text(ident.find("dcc:issuer", ns), info["identification_issuer"])
                set_text(ident.find("dcc:value", ns), info["calibration_item"])
                set_text(ident.find("dcc:name/dcc:content",   ns), info["serial_number"])
            desc = ci.find("dcc:description", ns)
            if desc is not None:
                cont = desc.findall("dcc:content", ns)
                set_text(cont[0], info["capacity"])
                set_text(cont[1], info["measurement_range"])
                set_text(cont[2], info["resolution"])

        # 4) second item (standard)
        if len(items) > 1:
            si_el = items[1]
            set_text(si_el.find("dcc:name/dcc:content", ns), info["standard_item"], lang=info["used_lang_code"])
            set_text(si_el.find("dcc:model", ns), info["standard_model"])
            ident2 = si_el.find("dcc:identifications/dcc:identification", ns)
            if ident2 is not None:
                set_text(ident2.find("dcc:issuer", ns), info["standard_item_issuer"])
                set_text(ident2.find("dcc:value", ns), info["standard_item"])
                set_text(ident2.find("dcc:name/dcc:content", ns), info["standard_serial_number"])
            desc2 = si_el.find("dcc:description", ns)
            if desc2 is not None:
                cont2 = desc2.findall("dcc:content", ns)
                set_text(cont2[0], info["standard_cert_number"])
                set_text(cont2[1], info["standard_traceability"])

        # 5) respPersons
        resp_nodes = root.findall(".//dcc:respPersons/dcc:respPerson", ns)
        for idx,(name,role) in enumerate([(info["resp_person1_name"],info["resp_person1_role"]),(info["resp_person2_name"],info["resp_person2_role"]),(info["resp_person3_name"],info["resp_person3_role"])]):
            if idx<len(resp_nodes):
                rp = resp_nodes[idx]
                set_text(rp.find("dcc:person/dcc:name/dcc:content", ns), name, lang=info["used_lang_code"])
                set_text(rp.find("dcc:role", ns), role)

        # 6) customer
        cust = root.find(".//dcc:customer", ns)
        set_text(cust.find("dcc:name/dcc:content", ns), info["customer_name"])
        f = cust.find("dcc:location/dcc:further/dcc:content", ns)
        set_text(f, info["customer_address"], lang=info["used_lang_code"])

        # 7) measurementResults
        mr = root.find(".//dcc:measurementResults", ns)
        set_text(mr.find("dcc:name/dcc:content", ns), info["calibration_item"], lang=info["used_lang_code"])
        um = mr.find("dcc:usedMethods/dcc:usedMethod", ns)
        set_text(um.find("dcc:name/dcc:content", ns), info["relative_uncertainty"], lang=info["used_lang_code"])
        set_text(um.find("dcc:description/dcc:content", ns), info["uncertainty_of_measurement"], lang=info["used_lang_code"])

        # 7) influenceConditions
        ic = mr.find(".//dcc:influenceConditions", ns)
        if ic is None:
            print("⚠️ influenceConditions not found")
        else:
            conds = ic.findall("dcc:influenceCondition", ns)
            # first condition
            if len(conds) > 0:
                infl = conds[0]
                set_text(infl.find("dcc:name/dcc:content", ns), "Ambient Temperature", lang=info["used_lang_code"])
                dq = infl.find(".//dcc:quantity", ns)
                set_text(dq.find("dcc:name/dcc:content", ns), "Ambient Temperature", lang=info["used_lang_code"])
                real = dq.find("si:real", ns)
                set_text(real.find("si:value", ns), info["temperature"])
                set_text(real.find("si:unit", ns), "\\" + info["temperature_unit"])
            # second condition
            if len(conds) > 1:
                infl = conds[1]
                set_text(infl.find("dcc:name/dcc:content", ns), "Relative Humidity", lang=info["used_lang_code"])
                dq = infl.find(".//dcc:quantity", ns)
                set_text(dq.find("dcc:name/dcc:content", ns), "Relative Humidity", lang=info["used_lang_code"])
                real = dq.find("si:real", ns)
                set_text(real.find("si:value", ns), info["humidity"])
                set_text(real.find("si:unit", ns), "\\" + info["humidity_unit"])

        # 8) results
        res = mr.find(".//dcc:results", ns)
        if res is None:
            print("⚠️ results not found")
        else:
            # now four rows per updated template:
            names = [
                info["measurement_standard"],
                info["measured_item"],
                info["measurement_error"],
                info["relative_uncertainty"],
                info["repeatability_error"]
            ]
            values = [
                info["standard_measurement_values"],
                info["measured_item_values"],
                info["measurement_error_values"],
                info["relative_uncertainty_values"],
                info["repeatability_error_values"]
            ]
            units = [
                info["standard_measurement_unit"],
                info["measured_item_unit"],
                info["measurement_error_unit"],
                info["relative_uncertainty_unit"],
                info["repeatability_error_unit"]
            ]
            for idx, row in enumerate(res.findall("dcc:result", ns)):
                set_text(row.find("dcc:name/dcc:content", ns),
                        names[idx],
                        lang=info["used_lang_code"])
                real_list = row.find(".//si:realListXMLList", ns)
                if real_list is not None:
                    set_text(real_list.find("si:valueXMLList", ns),
                            values[idx])
                    set_text(real_list.find("si:unitXMLList", ns),
                            units[idx])

        # 8) comment
        comm = root.find(".//dcc:comment", ns)
        cc = comm.findall("dcc:content", ns)
        if cc: 
            set_text(cc[0], "CALIBRATION PROCEDURE: " + info["calibration_procedure"], lang=info["used_lang_code"])
        if len(cc)>1: 
            set_text(cc[1], "REMARKS: " +info["remarks"], lang=info["used_lang_code"]) 
        # 5) laboratory, 6) persons, 7) conditions, 8) results, 9) comments…
        #    (copy each block from export_to_xml here, replacing `calibration_info` with `info`)

        return tree

    def build_xml_string():
        info = collect_calibration_info()
        tree = generate_xml_tree(info)
        buf = BytesIO()
        tree.write(buf, encoding="utf-8", xml_declaration=True)
        return buf.getvalue().decode("utf-8")



    def export_to_xml():
        # 1) collect raw UI inputs
        info = {
            #STATIC INFORMATION FROM JSON
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

            # Core data
            "certificate_number": "Calibration No. " + tsr_textbox.get(),
            "calibration_date": start_date_textbox.get(),
            "calibration_enddate": end_date_textbox.get(),
            "calibration_location": calibration_dropdown.get(),
            # Items
            "calibration_item": calibration_item_dropdown.get(),
            "make_model": model_textbox.get(),
            "serial_number": serial_number_textbox.get(),
            "capacity": "Capacity: " + capacity_textbox.get(),
            "measurement_range": "Measurement Range: " + range_textbox.get(),
            "resolution": "Resolution: " + resolution_textbox.get(),
            "identification_issuer": identification_issuer_textbox.get(),

            # Standard equipment
            "standard_item": standard_item_textbox1.get(),             # rename your widget if needed
            "standard_model": model_textbox1.get(),             # rename your widget if needed
            "standard_serial_number": serial_number_textbox1.get(),             # rename your widget if needed
            "standard_cert_number": "Calibration Certificate No.: " + calibCert_textbox.get(),             # rename your widget if needed    # example
            "standard_traceability": "Traceability: " +traceability_textbox.get(),
            "standard_item_issuer": identification_issuer_textbox1.get(),  # example

            # Persons
            "resp_person1_name": analyst1_textbox.get(),
            "resp_person1_role": role1_textbox.get(),
            "resp_person2_name": analyst2_textbox.get(),
            "resp_person2_role": role2_textbox.get(),
            "resp_person3_name": authorized_textbox.get(),
            "resp_person3_role": authorized_role_textbox.get(),

            # Customer
            "customer_name": customer_textbox.get(),
            "customer_address": address_textbox.get(),
            # Environment & results

            # measurement arrays – split on spaces or commas
            "temperature": temperature_textbox.get(),
            "temperature_unit": '\'' + temperature_unit_textbox.get(),
            "humidity": humidity_textbox.get(),
            "humidity_unit": '\'' + humidity_unit_textbox.get(),
            "standard_measurement_values": standard_measurement_textbox.get(),
            "standard_measurement_unit": standard_measurement_unit_textbox.get(),
            "measurement_standard": "Standard Measurement",
            "measured_item": "Indicated Measurement",
            "measured_item_values": indicated_measurement_textbox.get(),
            "measured_item_unit": indicated_measurement_unit_textbox.get(),
            "relative_uncertainty_values": relative_expanded_uncertainty_textbox.get(),
            "relative_uncertainty_unit": relative_expanded_uncertainty_unit_textbox.get(),
            "relative_uncertainty": "Relative Expanded Uncertainty",
            "measurement_error_values": measurement_error_textbox.get(),
            "measurement_error_unit": measurement_error_unit_textbox.get(),
            "measurement_error": "Measurement Error",
            "repeatability_error_values": repeatability_error_textbox.get(),
            "repeatability_error_unit": repeatability_error_unit_textbox.get(),
            "repeatability_error": "Repeatability Error",

            # big text‐areas
            "calibration_procedure": "CALIBRATION PROCEDURE: " + calibration_procedure_textbox.get("1.0", "end-1c").replace(placeholder_text, ""),
            "remarks": "REMARKS: " + remarks_textbox.get("1.0", "end-1c").replace(remarks_placeholder, ""),
            "uncertainty_of_measurement": uncertainty_textbox.get("1.0", "end-1c").replace(uncertainty_placeholder, ""),
        }
    
        # Import necessary libraries for XML processing

        # Define the template path
        template = os.path.join(script_dir, "template.xml")
        for p,u in {"dcc":"https://ptb.de/dcc","si":"https://ptb.de/si"}.items():
            ET.register_namespace(p,u)

        try:
            tree = ET.parse(template)
        except ParseError:
            parser = LET.XMLParser(recover=True)
            tree = LET.parse(template, parser)
        root = tree.getroot()

        def set_text(elem, txt, lang=None):
            if elem is None or txt is None: return
            elem.text = txt
            if lang: elem.set("lang", lang)

        ns = {"dcc":"https://ptb.de/dcc","si":"https://ptb.de/si"}

        # 1) software
        sw = root.find(".//dcc:software", ns)
        set_text(sw.find("dcc:name/dcc:content", ns), info["software_name"])
        set_text(sw.find("dcc:release", ns), info["software_release"])

        # 2) coreData
        cd = root.find(".//dcc:coreData", ns)
        set_text(cd.find("dcc:uniqueIdentifier", ns), info["certificate_number"])
        set_text(cd.find("dcc:beginPerformanceDate", ns), info["calibration_date"])
        set_text(cd.find("dcc:endPerformanceDate", ns), info["calibration_enddate"])
        set_text(cd.find("dcc:performanceLocation", ns), info["calibration_location"])

        # 3) first item (your device)
        items = root.findall(".//dcc:items/dcc:item", ns)
        if items:
            ci = items[0]
            set_text(ci.find("dcc:name/dcc:content", ns), info["calibration_item"], lang=info["used_lang_code"])
            set_text(ci.find("dcc:model", ns), info["make_model"])
            ident = ci.find("dcc:identifications/dcc:identification", ns)
            if ident is not None:
                set_text(ident.find("dcc:issuer", ns), info["identification_issuer"])
                set_text(ident.find("dcc:value", ns), info["calibration_item"])
                set_text(ident.find("dcc:name/dcc:content",   ns), info["serial_number"])
            desc = ci.find("dcc:description", ns)
            if desc is not None:
                cont = desc.findall("dcc:content", ns)
                set_text(cont[0], info["capacity"])
                set_text(cont[1], info["measurement_range"])
                set_text(cont[2], info["resolution"])

        # 4) second item (standard)
        if len(items) > 1:
            si_el = items[1]
            set_text(si_el.find("dcc:name/dcc:content", ns), info["standard_item"], lang=info["used_lang_code"])
            set_text(si_el.find("dcc:model", ns), info["standard_model"])
            ident2 = si_el.find("dcc:identifications/dcc:identification", ns)
            if ident2 is not None:
                set_text(ident2.find("dcc:issuer", ns), info["standard_item_issuer"])
                set_text(ident2.find("dcc:value", ns), info["standard_item"])
                set_text(ident2.find("dcc:name/dcc:content", ns), info["standard_serial_number"])
            desc2 = si_el.find("dcc:description", ns)
            if desc2 is not None:
                cont2 = desc2.findall("dcc:content", ns)
                set_text(cont2[0], info["standard_cert_number"])
                set_text(cont2[1], info["standard_traceability"])


        lab = root.find(".//dcc:calibrationLaboratory", ns)
        set_text(lab.find("dcc:calibrationLaboratoryCode", ns), info["calibration_labcode"])
        set_text(lab.find("dcc:contact/dcc:name/dcc:content", ns), info["calibration_contactname"])
        loc = lab.find("dcc:contact/dcc:location", ns)
        set_text(loc.find("dcc:city", ns), info["calibration_labcity"])
        set_text(loc.find("dcc:countryCode", ns), info["calibration_labcountrycode"])
        set_text(loc.find("dcc:postCode", ns), info["calibration_lab_postcode"])
        set_text(loc.find("dcc:street", ns), info["calibration_labstreet"])
        
        # 5) respPersons
        resp_nodes = root.findall(".//dcc:respPersons/dcc:respPerson", ns)
        for idx,(name,role) in enumerate([(info["resp_person1_name"],info["resp_person1_role"]),(info["resp_person2_name"],info["resp_person2_role"]),(info["resp_person3_name"],info["resp_person3_role"])]):
            if idx<len(resp_nodes):
                rp = resp_nodes[idx]
                set_text(rp.find("dcc:person/dcc:name/dcc:content", ns), name, lang=info["used_lang_code"])
                set_text(rp.find("dcc:role", ns), role)

        # 6) customer
        cust = root.find(".//dcc:customer", ns)
        set_text(cust.find("dcc:name/dcc:content", ns), info["customer_name"])
        f = cust.find("dcc:location/dcc:further/dcc:content", ns)
        set_text(f, info["customer_address"], lang=info["used_lang_code"])

        # 7) measurementResults
        mr = root.find(".//dcc:measurementResults", ns)
        set_text(mr.find("dcc:name/dcc:content", ns), info["calibration_item"], lang=info["used_lang_code"])
        um = mr.find("dcc:usedMethods/dcc:usedMethod", ns)
        set_text(um.find("dcc:name/dcc:content", ns), info["relative_uncertainty"], lang=info["used_lang_code"])
        set_text(um.find("dcc:description/dcc:content", ns), info["uncertainty_of_measurement"], lang=info["used_lang_code"])

        # 7) influenceConditions
        ic = mr.find(".//dcc:influenceConditions", ns)
        if ic is None:
            print("⚠️ influenceConditions not found")
        else:
            conds = ic.findall("dcc:influenceCondition", ns)
            # first condition
            if len(conds) > 0:
                infl = conds[0]
                set_text(infl.find("dcc:name/dcc:content", ns), "Ambient Temperature", lang=info["used_lang_code"])
                dq = infl.find(".//dcc:quantity", ns)
                set_text(dq.find("dcc:name/dcc:content", ns), "Ambient Temperature", lang=info["used_lang_code"])
                real = dq.find("si:real", ns)
                set_text(real.find("si:value", ns), info["temperature"])
                set_text(real.find("si:unit", ns), info["temperature_unit"])
            # second condition
            if len(conds) > 1:
                infl = conds[1]
                set_text(infl.find("dcc:name/dcc:content", ns), "Relative Humidity", lang=info["used_lang_code"])
                dq = infl.find(".//dcc:quantity", ns)
                set_text(dq.find("dcc:name/dcc:content", ns), "Relative Humidity", lang=info["used_lang_code"])
                real = dq.find("si:real", ns)
                set_text(real.find("si:value", ns), info["humidity"])
                set_text(real.find("si:unit", ns), info["humidity_unit"])

        # 8) results
        res = mr.find(".//dcc:results", ns)
        if res is None:
            print("⚠️ results not found")
        else:
            # now four rows per updated template:
            names = [
                info["measurement_standard"],
                info["measured_item"],
                info["measurement_error"],
                info["relative_uncertainty"],
                info["repeatability_error"]
            ]
            values = [
                info["standard_measurement_values"],
                info["measured_item_values"],
                info["measurement_error_values"],
                info["relative_uncertainty_values"],
                info["repeatability_error_values"]
            ]
            units = [
                info["standard_measurement_unit"],
                info["measured_item_unit"],
                info["measurement_error_unit"],
                info["relative_uncertainty_unit"],
                info["repeatability_error_unit"]
            ]
            for idx, row in enumerate(res.findall("dcc:result", ns)):
                set_text(row.find("dcc:name/dcc:content", ns),
                        names[idx],
                        lang=info["used_lang_code"])
                real_list = row.find(".//si:realListXMLList", ns)
                if real_list is not None:
                    set_text(real_list.find("si:valueXMLList", ns),
                            values[idx])
                    set_text(real_list.find("si:unitXMLList", ns),
                            units[idx])

        # 8) comment
        comm = root.find(".//dcc:comment", ns)
        cc = comm.findall("dcc:content", ns)
        if cc: 
            set_text(cc[0], "CALIBRATION PROCEDURE: " + info["calibration_procedure"], lang=info["used_lang_code"])
        if len(cc)>1: 
            set_text(cc[1], "REMARKS: " +info["remarks"], lang=info["used_lang_code"]) 

            # Let the user choose where to save the file
        suggested_filename = info["certificate_number"].replace(" ", "_") + "_DCC.xml"
        output_path = filedialog.asksaveasfilename(
            defaultextension=".xml",
            initialfile=suggested_filename,
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )

        # Check if user canceled the save dialog
        if not output_path:
            messagebox.showinfo("Operation Canceled", "File save operation canceled.")
            return

        # Ensure the directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Write the file
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        messagebox.showinfo("Success", f"XML file saved successfully to:\n{output_path}")

        back_to_menu()





    #### PREVIEW PANEL ####
    # 1) Create a right-hand preview panel with dark mode


    #### PREVIEW PANEL ####
    # 1) Create a right-hand preview panel with dark mode
    preview_frame = CTkFrame(
        master=app,
        fg_color="#2e2e2e",  # Dark background color
        border_color="black",
        border_width=1
    )
    preview_frame.place(relx=0.5, rely=0.0, relwidth=0.5, relheight=1.0)

    # 2) Create the preview textbox with dark mode
    preview_textbox = CTkTextbox(
        master=preview_frame,
        font=("Cascadia Code", 12),
        fg_color="#333333",  # Darker background for the textbox
        text_color="white",  # White text for contrast
        wrap="none"
    )
    preview_textbox.pack(fill="both", expand=True, padx=5, pady=5)

    # map each input widget to the XML tag name we want to scroll to
    widget_tag_map = {
        # coreData
        tsr_textbox:                   ("uniqueIdentifier", 0),
        start_date_textbox:            ("beginPerformanceDate", 0),
        end_date_textbox:              ("endPerformanceDate", 0),
        calibration_dropdown:          ("performanceLocation", 0),

        # first item
        calibration_item_dropdown:     ("name", 2),  # Target the item name
        model_textbox:                 ("identifications", 0),
        identification_issuer_textbox: ("description", 0),
        serial_number_textbox:         ("description", 0),
        capacity_textbox:              ("content", 3),
        range_textbox:                 ("content", 4),
        resolution_textbox:            ("content", 5),

        # second (standard)
        standard_item_textbox1:        ("name", 3),  # Target the standard item name
        model_textbox1:                ("model", 1),
        identification_issuer_textbox1:("identification", 3),
        serial_number_textbox1:        ("value", 1),
        calibCert_textbox:             ("content", 7),
        traceability_textbox:          ("content", 7),

        # persons
        analyst1_textbox:              ("respPerson", 0),
        role1_textbox:                 ("role", 0),
        analyst2_textbox:              ("respPerson", 1),
        role2_textbox:                 ("role", 1),
        authorized_textbox:            ("respPerson", 2),
        authorized_role_textbox:       ("role", 2),

        # customer
        customer_textbox:              ("location", 1),
        address_textbox:               ("further", 0),

        # conditions
        temperature_textbox:           ("value", 2),
        temperature_unit_textbox:      ("unit", 0),
        humidity_textbox:              ("value", 3),
        humidity_unit_textbox:         ("unit", 1),

        # results
        standard_measurement_textbox:   ("valueXMLList", 0),
        standard_measurement_unit_textbox:("unitXMLList", 0),
        indicated_measurement_textbox: ("valueXMLList", 1),
        indicated_measurement_unit_textbox:("unitXMLList", 1),
        measurement_error_textbox:   ("valueXMLList", 2),
        measurement_error_unit_textbox:("unitXMLList", 2),
        relative_expanded_uncertainty_textbox: ("valueXMLList", 3),
        relative_expanded_uncertainty_unit_textbox: ("unitXMLList", 3),
        repeatability_error_textbox: ("valueXMLList", 4),
        repeatability_error_unit_textbox: ("unitXMLList", 4),

        # big text areas
        uncertainty_textbox:           ("usedMethods", 0),
        calibration_procedure_textbox: ("comment", 0),
        remarks_textbox:               ("comment", 0),
    }

    # 2) update preview and scroll to the Nth occurrence
    import re
    def update_preview(active_widget=None):
        preview_textbox.configure(state="normal")
        xml = build_xml_string()
        preview_textbox.delete("1.0", "end")
        preview_textbox.insert("1.0", xml)
        preview_textbox.configure(state="disabled")

        # highlight inner text…
        text_widget = preview_textbox._textbox
        text_widget.tag_delete("content")
        text_widget.tag_config("content", foreground="#1E90FF")
        for m in re.finditer(r'>([^<]+)<', xml):
            text_widget.tag_add(
                "content",
                f"1.0 + {m.start(1)} chars",
                f"1.0 + {m.end(1)} chars"
            )

        # scroll to the Nth <tag>
        # inside update_preview(...)
            if active_widget in widget_tag_map:
                tag, idx = widget_tag_map[active_widget]
                # allow for optional namespace prefix (e.g. dcc: or si:)
                pattern = rf'<(?:\w+:)?{tag}\b'
                starts = [m.start() for m in re.finditer(pattern, xml)]
                if not starts:
                    return            # no such tag at all: bail
                # if idx too big, clamp to last occurrence instead of first
                pos = starts[min(idx, len(starts)-1)]
                text_widget.mark_set("insert", f"1.0 + {pos} chars")
                text_widget.see("insert")

    # 3) bind *all* inputs
    for child in scrollable_frame.winfo_children():
        if isinstance(child, CTkEntry):
            child._entry.bind("<KeyRelease>", lambda e, w=child: debounce_update_preview(w))
        elif isinstance(child, CTkTextbox):
            child._textbox.bind("<KeyRelease>", lambda e, w=child: debounce_update_preview(w))

    calibration_dropdown.configure(command=lambda *_: debounce_update_preview(calibration_dropdown))
    calibration_item_dropdown.configure(command=lambda *_: debounce_update_preview(calibration_item_dropdown))

    # 4) initial draw
    update_preview()

    # wire up the button
    exportButton.configure(command=export_to_xml) 

    app.mainloop()





