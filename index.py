from customtkinter import *
from PIL import Image
import os

app = CTk()
app.title("DCC")
app.geometry("500x400")
set_appearance_mode("dark")

# Functions
def open_cert():
    filename = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg")])
    certLabel.configure(text=filename)
    return filename

def open_format():
    filename = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
    formatLabel.configure(text=filename)
    return filename

def export_dcc():
    dcc = "DCC.xml"
    dccLabel.configure(text=dcc + " successfully generated")
    with open(dcc, 'w') as file:
        file.write("Certificate path: " + certLabel.cget("text") + "\n")
        file.write("Format path: " + formatLabel.cget("text") + "\n")
    return dcc

# Title label
titleLabel = CTkLabel(master=app, text="DCC Generator", font=("Arial", 32))
titleLabel.place(relx=0.15, rely=0.05)

# Textlabel for Import Calibration Certificate image
importCertL = CTkLabel(master=app, text="Select a Calibration Certificate Image", font=("Arial", 12))
importCertL.place(relx=0.15, rely=0.20)

# import button for image
importCert = CTkButton(master=app, text="Upload File", corner_radius=10, 
                    fg_color="#4158D0", hover_color="#C850C0", border_color="#FFCC70",
                    border_width=2, command=open_cert)
importCert.place(relx=0.15, rely=0.27)

# Textlabel for Certificate Image
certLabel = CTkLabel(master=app, text="exampleCertificate.jpg", font=("Arial", 12))
certLabel.place(relx=0.15, rely=.34)

# Textlabel for Import Calibration Certificate image
importFormatL = CTkLabel(master=app, text="Select Calibration Formal XML", font=("Arial", 12))
importFormatL.place(relx=0.15, rely=0.44)

# import button for xml
importFormat = CTkButton(master=app, text="Upload File", corner_radius=15,
                    fg_color="#4158D0", hover_color="#C850C0", border_color="#FFCC70",
                    border_width=2, command=open_format)
importFormat.place(relx=0.15, rely=0.53)

# Textlabel for Calibration Format XML
formatLabel = CTkLabel(master=app, text="exampleFormat.xml", font=("Arial", 12))
formatLabel.place(relx=0.15, rely=0.60)

# export button for DCC
exportDCC = CTkButton(master=app, text="Export DCC", corner_radius=15,
                    fg_color="#4158D0", hover_color="#C850C0", border_color="#FFCC70",
                    border_width=2, command=export_dcc)
exportDCC.place(relx=0.15, rely=0.75)

# Textlabel for DCC
dccLabel = CTkLabel(master=app, text="exampleDCC.xml", font=("Arial", 12))
dccLabel.place(relx=0.5, rely=0.75)

app.mainloop()

