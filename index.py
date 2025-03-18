from customtkinter import *

app = CTk()
app.title("DCC")
app.geometry("500x400")

file = ""

def open_cert():
    filename = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg")])
    certLabel.configure(text=filename)
    return filename

def open_xml():
    filename = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
    formatLabel.configure(text=filename)
    return filename

# def load():
#     with open(textField.get()) as file:
#         txt.SetValue(file.read())


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
                    border_width=2)
importFormat.place(relx=0.5, rely=0.50, anchor="center")

# Textlabel for Calibration Format XML
formatLabel = CTkLabel(master=app, text="exampleFormat.xml", font=("Arial", 12))
formatLabel.place(relx=0.5, rely=0.60, anchor="center")

# export button for DCC
exportDCC = CTkButton(master=app, text="Export DCC", corner_radius=15,
                    fg_color="#4158D0", hover_color="#C850C0", border_color="#FFCC70",
                    border_width=2)
exportDCC.place(relx=0.5, rely=0.70, anchor="center")

# Textlabel for DCC
dccLabel = CTkLabel(master=app, text="exampleDCC.xml", font=("Arial", 12))
dccLabel.place(relx=0.5, rely=0.80, anchor="center")

app.mainloop()

