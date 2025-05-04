from customtkinter import *
from PIL import Image
import os
from PIL import Image

app = CTk()
app.title("DigiCert")
app.geometry("375x160")
set_appearance_mode("light")

# Disable maximize button
app.resizable(False, False)

# Create a CTkFrame to act as the background (canvas)
bg_frame = CTkFrame(master=app, fg_color="white")  # Set the color to white
bg_frame.place(relx=0, rely=0, relwidth=1, relheight=1)  # Fill the entire window

# Description label
descLabel = CTkLabel(
    master=app,
    text="Your changes have been successfully saved to the XML schema.",
    font=("Inter", 12),
    anchor="center",  # Centers the text
    wraplength=200,
    bg_color='white'  # Wraps the text at 353px
)
descLabel.place(relx=0.029, rely=0.250, relwidth=0.942, relheight=0.200)

# Back button
backButton = CTkButton(master=app, text="Ok", corner_radius=7, 
                    fg_color="#010E54", hover_color="#1A4F8B", font=("Inter", 12, "bold"), command=app.destroy)
backButton.place(relx=0.352, rely=0.590, relwidth=0.296, relheight=0.20625)



app.mainloop()