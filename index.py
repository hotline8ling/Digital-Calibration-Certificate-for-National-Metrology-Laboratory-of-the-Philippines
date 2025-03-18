from customtkinter import *
import os

app = CTk()
app.title("DCC")
app.geometry("500x400")
set_appearance_mode("dark")

# Store values
# cert_path = ""
# format_path = ""

def open_cert():
    filename = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg")])
    certLabel.configure(text=filename)
    cert = filename
    return filename

def open_format():
    filename = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
    formatLabel.configure(text=filename)
    format = filename
    return filename

def export_dcc():
    dcc = "DCC.xml"
    dccLabel.configure(text="DCC successfuly generated named " + dcc)
    with open(dcc, 'w') as file:
        file.write("Certificate path: " + certLabel.cget("text") + "\n")
        file.write("Format path: " + formatLabel.cget("text") + "\n")
    return dcc

# Title label
titleLabel = CTkLabel(master=app, text="DCC Generator", font=("Arial", 24))
titleLabel.place(relx=0.5, rely=0.10, anchor="center")

# import button for image
importCert = CTkButton(master=app, text="Select Calibration Certificate Image", corner_radius=15, 
                    fg_color="#4158D0", hover_color="#C850C0", border_color="#FFCC70",
                    border_width=2, command=open_cert)

importCert.place(relx=0.5, rely=0.30, anchor="center")

# Textlabel for Calibration Certificate image
certLabel = CTkLabel(master=app, text="exampleCertificate.xml", font=("Arial", 12))
certLabel.place(relx=0.5, rely=0.40, anchor="center")

# import button for xml
importFormat = CTkButton(master=app, text="Select Calibration Format XML", corner_radius=15,
                    fg_color="#4158D0", hover_color="#C850C0", border_color="#FFCC70",
                    border_width=2, command=open_format)
importFormat.place(relx=0.5, rely=0.50, anchor="center")

# Textlabel for Calibration Format XML
formatLabel = CTkLabel(master=app, text="exampleFormat.xml", font=("Arial", 12))
formatLabel.place(relx=0.5, rely=0.60, anchor="center")

# export button for DCC
exportDCC = CTkButton(master=app, text="Export DCC", corner_radius=15,
                    fg_color="#4158D0", hover_color="#C850C0", border_color="#FFCC70",
                    border_width=2, command=export_dcc)
exportDCC.place(relx=0.5, rely=0.70, anchor="center")

# Textlabel for DCC
dccLabel = CTkLabel(master=app, text="exampleDCC.xml", font=("Arial", 12))
dccLabel.place(relx=0.5, rely=0.80, anchor="center")

app.mainloop()

