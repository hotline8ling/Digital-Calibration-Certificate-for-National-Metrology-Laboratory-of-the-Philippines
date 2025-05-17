import subprocess
from customtkinter import *
from PIL import Image
import os
from PIL import Image
import json

def runapp():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'static_info.json')
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
        subprocess.Popen(["python",  os.path.join(os.path.dirname(__file__),"index.py")])


    # app = CTk()
    # app.title("DigiCert")
    # app.geometry("500x600")
    # set_appearance_mode("light")

    # # Disable maximize button
    # app.resizable(False, False)


    # Center the application on the screen
    def center_window(app, width, height):
        app.update_idletasks()
        screen_width = app.winfo_screenwidth()
        screen_height = app.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        app.geometry(f"{width}x{height}+{x}+{y}")

    app = CTk()
    app.title("DigiCert")
    app_width = 500
    app_height = 600
    center_window(app, app_width, app_height)  # Call the function to center the window
    set_appearance_mode("light")

    # Disable maximize button
    app.resizable(False, False)

    # Create a CTkFrame to act as the background (canvas)
    bg_frame = CTkFrame(master=app, fg_color="white") 
    bg_frame.place(relx=0, rely=0, relwidth=1, relheight=1)  

    # Load and Resize the Image
    image = CTkImage(light_image=Image.open(os.path.join(script_dir, "itdi-logo.png")), size=(26, 25))
    # Create CTkLabel with Image
    image_label = CTkLabel(master=app, image=image, text="", bg_color='white') 
    image_label.place(relx=0.886, rely=0.0533)

    # Load and Resize the Image
    image1 = CTkImage(light_image=Image.open(os.path.join(script_dir,"nml-logo1.png")), size=(29, 28))
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
    editCountry.insert(0, cfg["calibration_lab"]["countrycode"])
    editCountry.configure(state="disabled")

    # Textlabel Language
    editLanguage = CTkLabel(master=app, text="Language:", font=("Inter", 13, "bold"), bg_color="#E0E0E0")
    editLanguage.place(relx=0.124, rely=0.305)


    # Textbox Language
    editLanguage = CTkEntry(master=app, font=("Inter", 13), fg_color="white", bg_color="#E0E0E0", placeholder_text="e.g. en")
    editLanguage.place(relx=0.124, rely=0.35, relwidth=0.368, relheight=0.066)
    editLanguage.insert(0, cfg["used_lang_code"])
    editLanguage.configure(state="disabled")

    # Calibration Equipment Label
    labLabel = CTkLabel(master=app, text="Calibration Laboratory", font=("Montserrat", 13, "bold"), bg_color='white')
    labLabel.place(relx=0.126, rely=0.443)

    # arrow icon
    arrow_image = CTkImage(light_image=Image.open(os.path.join(script_dir,"arrow.png")), size=(11, 11))
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
    editCity.insert(0, cfg["calibration_lab"]["city"])
    editCity.configure(state="disabled")

    # Textlabel Laboratory
    LabLabel = CTkLabel(master=app, text="City:", font=("Montserrat", 13, "bold"), bg_color="#E0E0E0")
    LabLabel.place(relx=0.566, rely=0.530)

    # Textbox Laboratory
    editLab = CTkEntry(master=app, font=("Inter", 13), fg_color="white", bg_color="#E0E0E0", placeholder_text="e.g. NML-ITDI")
    editLab.place(relx=0.566, rely=0.571, relwidth=0.368, relheight=0.066)
    editLab.insert(0, cfg["calibration_lab"]["contact"])
    editLab.configure(state="disabled")

    # Textlabel Postal Code
    postalCodeLabel = CTkLabel(master=app, text="Postal Code:", font=("Montserrat", 13, "bold"), bg_color="#E0E0E0")
    postalCodeLabel.place(relx=0.142, rely=0.647)

    # Textbox Postal Code
    editPostal = CTkEntry(master=app, font=("Inter", 13), fg_color="white", bg_color="#E0E0E0", placeholder_text="e.g. 1633")
    editPostal.place(relx=0.142, rely=0.685, relwidth=0.368, relheight=0.066)
    editPostal.insert(0, cfg["calibration_lab"]["postcode"])
    editPostal.configure(state="disabled")

    # Textlabel Laboratory Code
    labCodeLabel = CTkLabel(master=app, text="Laboratory Code:", font=("Montserrat", 13, "bold"), bg_color="#E0E0E0")
    labCodeLabel.place(relx=0.566, rely=0.647)

    # Textbox Laboratory Code
    editLabCode = CTkEntry(master=app, font=("Inter", 13), fg_color="white", bg_color="#E0E0E0", placeholder_text="e.g. FORC")
    editLabCode.place(relx=0.566, rely=0.685, relwidth=0.368, relheight=0.066)
    editLabCode.insert(0, cfg["calibration_lab"]["code"])
    editLabCode.configure(state="disabled")

    # Textlabel Street
    streetLabel = CTkLabel(master=app, text="Street:", font=("Montserrat", 13, "bold"), bg_color="#E0E0E0")
    streetLabel.place(relx=0.142, rely=0.753)

    # Textbox Street
    editStreet = CTkEntry(master=app, font=("Inter", 13), fg_color="white", bg_color="#E0E0E0", placeholder_text="e.g. General Santos Ave")
    editStreet.place(relx=0.142, rely=0.790, relwidth=0.368, relheight=0.066)
    editStreet.insert(0, cfg["calibration_lab"]["street"])
    editStreet.configure(state="disabled")

    def edit_fields():
        # Enable the fields for editing
        editCountry.configure(state="normal")
        editLanguage.configure(state="normal")
        editCity.configure(state="normal")
        editLab.configure(state="normal")
        editPostal.configure(state="normal")
        editLabCode.configure(state="normal")
        editStreet.configure(state="normal")
        # Change the button text to "Save Changes"

        editButton.configure(text="Save Changes", command=save_fields)


    def save_fields():
        # Get the values from the fields
        country = editCountry.get()
        language = editLanguage.get()
        city = editCity.get()
        lab = editLab.get()
        postal = editPostal.get()
        lab_code = editLabCode.get()
        street = editStreet.get()

        # Update the JSON configuration file with the new values
        cfg["calibration_lab"]["countrycode"] = country
        cfg["used_lang_code"] = language
        cfg["calibration_lab"]["city"] = city
        cfg["calibration_lab"]["contact"] = lab
        cfg["calibration_lab"]["postcode"] = postal
        cfg["calibration_lab"]["code"] = lab_code
        cfg["calibration_lab"]["street"] = street

        with open(config_path, 'w') as file:
            json.dump(cfg, file, indent=4)

        # Disable the fields again after saving
        editCountry.configure(state="disabled")
        editLanguage.configure(state="disabled")
        editCity.configure(state="disabled")
        editLab.configure(state="disabled")
        editPostal.configure(state="disabled")
        editLabCode.configure(state="disabled")
        editStreet.configure(state="disabled")
        
        # Change button text back to "Edit"
        editButton.configure(text="Edit", command=edit_fields)


    # Edit button
    editButton = CTkButton(master=app, text="Edit", corner_radius=7, 
                        fg_color="#010E54", hover_color="#1A4F8B", font=("Inter", 13), command=edit_fields)
    editButton.place(relx=0.384, rely=0.9, relwidth=0.242, relheight=0.055)

    # Back button
    backButton = CTkButton(master=app, text="< ", corner_radius=7, 
                        fg_color="#010E54", hover_color="#1A4F8B", font=("Inter", 15), command=back_to_menu)
    backButton.place(relx=0.044, rely=0.06, relwidth=0.05, relheight=0.0417)




    app.mainloop()