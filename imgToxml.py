from customtkinter import *
from PIL import Image
import os
from PIL import Image
import os

app = CTk()
app.title("DigiCert")
app.geometry("600x700")
set_appearance_mode("light")

# Disable maximize button
app.resizable(False, False)

# Create a CTkFrame to act as the background (canvas)
bg_frame = CTkFrame(master=app, fg_color="white") 
bg_frame.place(relx=0, rely=0, relwidth=1, relheight=1)  

# Compute relx and rely based on 58x84 starting point in a 600x700 canvas
relx = 58 / 600
rely = 84 / 700 
relwidth = 475 / 600  
relheight = 525 / 700  

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

# Manufacturer Name Label
manufacturer_name_label = CTkLabel(master=scrollable_frame, text="Manufacturer Name:", font=("Inter", 12, "bold"), bg_color='white')
manufacturer_name_label.grid(row=10, column=0, padx=10, pady=(5, 5), sticky="w")

# Manufacturer Name Textbox
manufacturer_name_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. Not given")
manufacturer_name_textbox.grid(row=11, column=0, padx=10, pady=(5, 10), sticky="w")

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
identification_issuer_label.grid(row=14, column=0, padx=10, pady=(5, 5), sticky="w")

# Identification Issuer Textbox
identification_issuer_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. customer")
identification_issuer_textbox.grid(row=15, column=0, padx=10, pady=(5, 10), sticky="w")

# Resolution Label
resolution_label = CTkLabel(master=scrollable_frame, text="Resolution:", font=("Inter", 12, "bold"), bg_color='white')
resolution_label.grid(row=14, column=1, padx=10, pady=(5, 5), sticky="w")

# Resolution Textbox
resolution_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. 50 kgf")
resolution_textbox.grid(row=15, column=1, padx=10, pady=(5, 10), sticky="w")

##########################
# Standard Equipment Label
standard_equipment_label = CTkLabel(master=scrollable_frame, text="Standard Equipment:", font=("Inter", 14, "bold"), bg_color='white')
standard_equipment_label.grid(row=16, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

# Standard Item Label
standard_item_label = CTkLabel(master=scrollable_frame, text="Standard Item:", font=("Inter", 12, "bold"), bg_color='white')
standard_item_label.grid(row=17, column=0, padx=10, pady=(5, 5), sticky="w")

# Standard Item Textbox
standard_item_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. Force Measuring Equipment")
standard_item_textbox.grid(row=18, column=0, padx=10, pady=(5, 10), sticky="w")

# Serial Number Label
serial_number_label = CTkLabel(master=scrollable_frame, text="Serial Number:", font=("Inter", 12, "bold"), bg_color='white')
serial_number_label.grid(row=17, column=1, padx=10, pady=(5, 5), sticky="w")

# Serial Number Textbox
serial_number_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. SN 1251056K0094")
serial_number_textbox.grid(row=18, column=1, padx=10, pady=(5, 10), sticky="w")

# Manufacturer Name Label
manufacturer_name_label = CTkLabel(master=scrollable_frame, text="Manufacturer Name:", font=("Inter", 12, "bold"), bg_color='white')
manufacturer_name_label.grid(row=19, column=0, padx=10, pady=(5, 5), sticky="w")

# Manufacturer Name Textbox
manufacturer_name_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. Not given")
manufacturer_name_textbox.grid(row=20, column=0, padx=10, pady=(5, 10), sticky="w")

# Calibration Cert Label
calibCert_label = CTkLabel(master=scrollable_frame, text="Calibration Certificate No.", font=("Inter", 12, "bold"), bg_color='white')
calibCert_label.grid(row=19, column=1, padx=10, pady=(5, 5), sticky="w")

# Calibration Cert Textbox
calibCert_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. 11-2020-FORC-0116")
calibCert_textbox.grid(row=20, column=1, padx=10, pady=(5, 10), sticky="w")

# Model Label
model_label = CTkLabel(master=scrollable_frame, text="Model:", font=("Inter", 12, "bold"), bg_color='white')
model_label.grid(row=21, column=0, padx=10, pady=(5, 5), sticky="w")

# Model Textbox
model_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. Shimadzu/ UH-F1000kNX")
model_textbox.grid(row=22, column=0, padx=10, pady=(5, 10), sticky="w")

# Traceability Label
traceability_label = CTkLabel(master=scrollable_frame, text="Traceability:", font=("Inter", 12, "bold"), bg_color='white')
traceability_label.grid(row=21, column=1, padx=10, pady=(5, 5), sticky="w")

# Traceability Textbox
traceability_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. Traceable to the SI through NMD-ITDI")
traceability_textbox.grid(row=22, column=1, padx=10, pady=(5, 10), sticky="w")

# Identification Issuer Label
identification_issuer_label = CTkLabel(master=scrollable_frame, text="Identification Issuer:", font=("Inter", 12, "bold"), bg_color='white')
identification_issuer_label.grid(row=23, column=0, padx=10, pady=(5, 5), sticky="w")

# Identification Issuer Textbox
identification_issuer_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. laboratory")
identification_issuer_textbox.grid(row=24, column=0, padx=10, pady=(5, 10), sticky="w")

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
temperature_unit_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. \celcius")
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
humidity_unit_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. \%")
humidity_unit_textbox.grid(row=39, column=1, padx=10, pady=(5, 10), sticky="w")

##########################
# Results Label
results_label = CTkLabel(master=scrollable_frame, text="Results:", font=("Inter", 14, "bold"), bg_color='white')
results_label.grid(row=40, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

# Applied Measurement Label
applied_measurement_label = CTkLabel(master=scrollable_frame, text="Applied Measurement:", font=("Inter", 12, "bold"), bg_color='white')
applied_measurement_label.grid(row=41, column=0, padx=10, pady=(5, 5), sticky="w")

# Applied Force Textbox
applied_measurement_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. 0.00 3 000 6 000")
applied_measurement_textbox.grid(row=42, column=0, padx=10, pady=(5, 10), sticky="w")

# Unit Label (Applied Force)
applied_force_unit_label = CTkLabel(master=scrollable_frame, text="Unit:", font=("Inter", 12, "bold"), bg_color='white')
applied_force_unit_label.grid(row=41, column=1, padx=10, pady=(5, 5), sticky="w")

# Unit Textbox (Applied Force)
applied_force_unit_textbox = CTkEntry(master=scrollable_frame, font=("Inter", 12), fg_color='white', border_width=2, width=170, height=30, placeholder_text="e.g. \kgf \kgf \kgf")
applied_force_unit_textbox.grid(row=42, column=1, padx=10, pady=(5, 10), sticky="w")

# Indicated Force Label
indicated_force_label = CTkLabel(master=scrollable_frame, text="Indicated Measurement:", font=("Inter", 12, "bold"), bg_color='white')
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
# Uncertainty of Measurement Label
uncertainty_label = CTkLabel(master=scrollable_frame, text="Uncertainty of Measurement:", font=("Inter", 14, "bold"), bg_color='white')
uncertainty_label.grid(row=47, column=0, padx=10, pady=(5, 5), sticky="w")

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
uncertainty_textbox.grid(row=48, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="we")


#############################
# Calibration Procedure Label
calibration_procedure_label = CTkLabel(master=scrollable_frame, text="Calibration Procedure:", font=("Inter", 14, "bold"), bg_color='white')
calibration_procedure_label.grid(row=49, column=0, padx=10, pady=(5, 5), sticky="w")

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
calibration_procedure_textbox.grid(row=50, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="we")


###############
# Remarks Label
remarks_label = CTkLabel(master=scrollable_frame, text="Remarks:", font=("Inter", 14, "bold"), bg_color='white')
remarks_label.grid(row=51, column=0, padx=10, pady=(5, 5), sticky="w")

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
remarks_textbox.grid(row=52, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="we")



# ^ content of scrollable frame
#########################################

script_dir = os.path.dirname(os.path.abspath(__file__))
# Load and Resize the Image
itdi_logo_path = os.path.join(script_dir, "itdi-logo.png")
image = CTkImage(light_image=Image.open(itdi_logo_path), size=(26, 25))

# Create CTkLabel with Image
image_label = CTkLabel(master=app, image=image, text="", bg_color='white') 
image_label.place(relx=1.0, rely=0.0457)

script_dir = os.path.dirname(os.path.abspath(__file__))
# Load and Resize the Image
nml_logo_path = os.path.join(script_dir, "nml-logo1.png")
image1 = CTkImage(light_image=Image.open(nml_logo_path), size=(29, 28))

# Create CTkLabel with Image
image_label = CTkLabel(master=app, image=image1, text="", bg_color='white') 
image_label.place(relx=1.0, rely=0.0457)

stroke = CTkFrame(master=app, fg_color="#0855B1", corner_radius=0)
stroke.place(relx=0.0967, rely=0.0443, relwidth=0.012, relheight=0.045)

# Title label
titleLabel = CTkLabel(master=app, text="DigiCert", font=("Montserrat", 32, "bold"), bg_color='white')
titleLabel.place(relx=0.1133, rely=0.0330)

# BG rectangle 
footer_frame = CTkFrame(master=app, fg_color="#E0E0E0", corner_radius=0)
footer_frame.place(relx=0.0, rely=0.89, relwidth=1.0, relheight=0.1114)

# Save Edit button
saveEButton = CTkButton(master=app, text="Preview", corner_radius=7, 
                       fg_color="#000000", hover_color="#1A4F8B", font=("Inter", 13))
saveEButton.place(relx=0.2834, rely=0.9220, relwidth=0.2016, relheight=0.0471)

# Export button
exportButton = CTkButton(master=app, text="Export", corner_radius=7, 
                         fg_color="#010E54", hover_color="#1A4F8B", font=("Inter", 13))
exportButton.place(relx=0.5150, rely=0.9220, relwidth=0.2016, relheight=0.0471)

# Back button
backButton = CTkButton(master=app, text="< ", corner_radius=7, 
                    fg_color="#010E54", hover_color="#1A4F8B", font=("Inter", 15))
backButton.place(relx=0.0450, rely=0.0486, relwidth=0.0400, relheight=0.0350)

# IMG to XML label
titleLabel = CTkLabel(master=app, text="IMG -> XML", font=("Inter", 13, "bold"), bg_color='white')
titleLabel.place(relx=0.3600, rely=0.0514)

app.mainloop()