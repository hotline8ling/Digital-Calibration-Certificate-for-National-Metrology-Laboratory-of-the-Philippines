from customtkinter import *
from PIL import Image
import os
from PIL import Image

app = CTk()
app.title("DCC")
app.geometry("500x400")
set_appearance_mode("light")

# Functions
def open_cert():
    filename = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg")])
    global img_path
    img_path = filename
    certLabel.configure(text=os.path.basename(filename))
    return filename

def open_format():
    filename = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
    global format_path
    format_path = filename
    formatLabel.configure(text=os.path.basename(filename))
    return filename

def export_dcc():
    dcc = "DCC.xml"
    dccLabel.configure(text=dcc + " successfully generated")
    with open(dcc, 'w') as file:
        # file.write("Certificate path: " + certLabel.cget("text") + "\n")
        # file.write("Format path: " + formatLabel.cget("text") + "\n")
        file.write("Certificate path: " + img_path + "\n")
        file.write("Format path: " + format_path + "\n")
    return dcc

# Load and Resize the Image
image = CTkImage(light_image=Image.open("itdi-logo.png"), size=(26, 25))
# Create CTkLabel with Image
image_label = CTkLabel(master=app, image=image, text="") 
image_label.place(relx=0.886, rely=0.085) 

# Load and Resize the Image
image1 = CTkImage(light_image=Image.open("nml-logo.png"), size=(26, 25))
# Create CTkLabel with Image
image_label = CTkLabel(master=app, image=image1, text="") 
image_label.place(relx=0.814, rely=0.0775) 

stroke = CTkFrame(master=app, fg_color="#0855B1", corner_radius=0)
stroke.place(relx=0.096, rely=0.0925, relwidth=0.006, relheight=0.0675)

# Adding Background Rectangle (Using CTkFrame)
bg_frame = CTkFrame(master=app, fg_color="#E0E0E0", corner_radius=0)
bg_frame.place(relx=0, rely=0.2175, relwidth=1, relheight=0.2525)

# Adding Background Rectangle (Using CTkFrame)
bg_frame2 = CTkFrame(master=app, fg_color="#E0E0E0", corner_radius=0)
bg_frame2.place(relx=0, rely=0.4875, relwidth=1, relheight=0.2525)

# Title label
titleLabel = CTkLabel(master=app, text="DCC Generator", font=("Montserrat", 32, "bold"))
titleLabel.place(relx=0.112, rely=0.065)

# Textlabel for Import Calibration Certificate image
importCertL = CTkLabel(master=app, text="Select a Calibration Certificate Image", font=("Inter", 13), bg_color="#E0E0E0")
importCertL.place(relx=0.124, rely=0.23)

# import button for image
importCert = CTkButton(master=app, text="Upload File", corner_radius=7, 
                    fg_color="#0855B1", hover_color="#010E54", command=open_cert)
importCert.place(relx=0.124, rely=0.30, relwidth=0.368, relheight=0.0825)

# Textlabel for Certificate Image
certLabel = CTkLabel(master=app, text="exampleCertificate.jpg", font=("Inter", 12), bg_color="#E0E0E0")
certLabel.place(relx=0.124, rely=0.38)

# Textlabel for Import Calibration Certificate image
importFormatL = CTkLabel(master=app, text="Select Calibration Formal XML", font=("Inter", 13), bg_color="#E0E0E0")
importFormatL.place(relx=0.124, rely=0.5025)

# import button for xml
importFormat = CTkButton(master=app, text="Upload File", corner_radius=7,
                    fg_color="#0855B1", hover_color="#010E54", command=open_format)
importFormat.place(relx=0.124, rely=0.57, relwidth=0.368, relheight=0.0825)

# Textlabel for Calibration Format XML
formatLabel = CTkLabel(master=app, text="exampleFormat.xml", font=("Inter", 12), bg_color="#E0E0E0")
formatLabel.place(relx=0.124, rely=0.65)

# export button for DCC
exportDCC = CTkButton(master=app, text="Export DCC", corner_radius=7,
                    fg_color="#0855B1", hover_color="#010E54", command=export_dcc)
exportDCC.place(relx=0.124, rely=0.785, relwidth=0.222, relheight=0.0825)

# Textlabel for DCC
dccLabel = CTkLabel(master=app, text="exampleDCC.xml", font=("Inter", 12))
dccLabel.place(relx=0.37, rely=0.7925)

app.mainloop()