from customtkinter import *
from PIL import Image
import os
from PIL import Image

app = CTk()
app.title("DigiCert")
app.geometry("1200x700")
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

# Create a scrollable frame
scrollable_frame = CTkScrollableFrame(master=app)
scrollable_frame.place(relx=relx, rely=rely, relwidth=relwidth, relheight=relheight)

# Add widgets inside the scrollable frame
for i in range(30):
    label = CTkLabel(scrollable_frame, text=f"Item {i+1}")
    label.pack(pady=5)

# Load and Resize the Image
image = CTkImage(light_image=Image.open("itdi-logo.png"), size=(26, 25))
# Create CTkLabel with Image
image_label = CTkLabel(master=app, image=image, text="", bg_color='white') 
image_label.place(relx=0.4525, rely=0.0457)

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


app.mainloop()