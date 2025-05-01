from customtkinter import *
from PIL import Image
import os
from PIL import Image

app = CTk()
app.title("DigiCert")
app.geometry("500x600")
set_appearance_mode("light")

# Disable maximize button
app.resizable(False, False)

# Create a CTkFrame to act as the background (canvas)
bg_frame = CTkFrame(master=app, fg_color="white") 
bg_frame.place(relx=0, rely=0, relwidth=1, relheight=1)  

# Load and Resize the Image
image = CTkImage(light_image=Image.open("itdi-logo.png"), size=(26, 25))
# Create CTkLabel with Image
image_label = CTkLabel(master=app, image=image, text="", bg_color='white') 
image_label.place(relx=0.886, rely=0.0533)

# Load and Resize the Image
image1 = CTkImage(light_image=Image.open("nml-logo1.png"), size=(29, 28))
# Create CTkLabel with Image
image_label = CTkLabel(master=app, image=image1, text="", bg_color='white') 
image_label.place(relx=0.814, rely=0.0533)

stroke = CTkFrame(master=app, fg_color="#0855B1", corner_radius=0)
stroke.place(relx=0.106, rely=0.0550, relwidth=0.006, relheight=0.045)

# Title label
titleLabel = CTkLabel(master=app, text="DigiCert", font=("Montserrat", 32, "bold"), bg_color='white')
titleLabel.place(relx=0.126, rely=0.038)

# Description label
titleLabel = CTkLabel(master=app, text="Edit Static Information", font=("Montserrat", 20, "bold"), bg_color='white')
titleLabel.place(relx=0.126, rely=0.113)

# BG rectangle 1
bg_frame = CTkFrame(master=app, fg_color="#E0E0E0", corner_radius=0)
bg_frame.place(relx=0, rely=0.185, relwidth=1, relheight=0.255)

# Textlabel Country
editCert = CTkLabel(master=app, text="Country:", font=("Inter", 13, "bold"), bg_color="#E0E0E0")
editCert.place(relx=0.124, rely=0.200)

# Textbox Country
editCountry = CTkEntry(master=app, font=("Inter", 13), fg_color="white", bg_color="#E0E0E0", placeholder_text="e.g. PH")
editCountry.place(relx=0.124, rely=0.24, relwidth=0.368, relheight=0.066)

# Textlabel Language
editLanguage = CTkLabel(master=app, text="Language:", font=("Inter", 13, "bold"), bg_color="#E0E0E0")
editLanguage.place(relx=0.124, rely=0.305)

# Textbox Language
editLanguage = CTkEntry(master=app, font=("Inter", 13), fg_color="white", bg_color="#E0E0E0", placeholder_text="e.g. en")
editLanguage.place(relx=0.124, rely=0.35, relwidth=0.368, relheight=0.066)

# Calibration Equipment Label
labLabel = CTkLabel(master=app, text="Calibration Laboratory", font=("Montserrat", 13, "bold"), bg_color='white')
labLabel.place(relx=0.126, rely=0.443)

# arrow icon
arrow_image = CTkImage(light_image=Image.open("arrow.png"), size=(11, 11))
arrow_label = CTkLabel(master=app, image=arrow_image, text="", bg_color='white')
arrow_label.place(relx=0.090, rely=0.443)

# BG rectangle 2
bg_frame = CTkFrame(master=app, fg_color="#E0E0E0", corner_radius=0)
bg_frame.place(relx=0, rely=0.492, relwidth=1, relheight=0.38)

# Lab Address Label
labLabel = CTkLabel(master=app, text="Laboratory Address:", font=("Montserrat", 13, "bold"), bg_color="#E0E0E0")
labLabel.place(relx=0.124, rely=0.498)

# Textlabel City
cityLabel = CTkLabel(master=app, text="City:", font=("Montserrat", 13, "bold"), bg_color="#E0E0E0")
cityLabel.place(relx=0.142, rely=0.530)

# Textbox Language
editCity = CTkEntry(master=app, font=("Inter", 13), fg_color="white", bg_color="#E0E0E0", placeholder_text="e.g. Taguig")
editCity.place(relx=0.142, rely=0.571, relwidth=0.368, relheight=0.066)

# Textlabel Laboratory
LabLabel = CTkLabel(master=app, text="City:", font=("Montserrat", 13, "bold"), bg_color="#E0E0E0")
LabLabel.place(relx=0.566, rely=0.530)

# Textbox Laboratory
editLab = CTkEntry(master=app, font=("Inter", 13), fg_color="white", bg_color="#E0E0E0", placeholder_text="e.g. NML-ITDI")
editLab.place(relx=0.566, rely=0.571, relwidth=0.368, relheight=0.066)

# Textlabel Postal Code
postalCodeLabel = CTkLabel(master=app, text="Postal Code:", font=("Montserrat", 13, "bold"), bg_color="#E0E0E0")
postalCodeLabel.place(relx=0.142, rely=0.647)

# Textbox Postal Code
editPostal = CTkEntry(master=app, font=("Inter", 13), fg_color="white", bg_color="#E0E0E0", placeholder_text="e.g. 1633")
editPostal.place(relx=0.142, rely=0.685, relwidth=0.368, relheight=0.066)

# Textlabel Laboratory Code
labCodeLabel = CTkLabel(master=app, text="Laboratory Code:", font=("Montserrat", 13, "bold"), bg_color="#E0E0E0")
labCodeLabel.place(relx=0.566, rely=0.647)

# Textbox Laboratory Code
editLabCode = CTkEntry(master=app, font=("Inter", 13), fg_color="white", bg_color="#E0E0E0", placeholder_text="e.g. FORC")
editLabCode.place(relx=0.566, rely=0.685, relwidth=0.368, relheight=0.066)

# Textlabel Street
streetLabel = CTkLabel(master=app, text="Street:", font=("Montserrat", 13, "bold"), bg_color="#E0E0E0")
streetLabel.place(relx=0.142, rely=0.753)

# Textbox Street
editStreet = CTkEntry(master=app, font=("Inter", 13), fg_color="white", bg_color="#E0E0E0", placeholder_text="e.g. General Santos Ave")
editStreet.place(relx=0.142, rely=0.790, relwidth=0.368, relheight=0.066)

# Edit button
editButton = CTkButton(master=app, text="Edit", corner_radius=7, 
                       fg_color="#000000", hover_color="#1A4F8B", font=("Inter", 13))
editButton.place(relx=0.244, rely=0.9017, relwidth=0.242, relheight=0.055)

# Save button
saveButton = CTkButton(master=app, text="Save Changes", corner_radius=7, 
                    fg_color="#010E54", hover_color="#1A4F8B", font=("Inter", 13))
saveButton.place(relx=0.512, rely=0.902, relwidth=0.242, relheight=0.055)

# Back button
backButton = CTkButton(master=app, text="< ", corner_radius=7, 
                    fg_color="#010E54", hover_color="#1A4F8B", font=("Inter", 15))
backButton.place(relx=0.044, rely=0.06, relwidth=0.05, relheight=0.0417)


app.mainloop()