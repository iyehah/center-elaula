import customtkinter as ctk
from tkinter import PhotoImage
from PIL import Image, ImageTk

class Developer(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)
        
        # Load images safely
        try:
            # Convert image to PhotoImage using PIL
            pil_image = Image.open("dev.png").resize((80, 80), Image.Resampling.LANCZOS)
            self.user_image = ImageTk.PhotoImage(pil_image)

            # Profile Image
            self.profile_image_label = ctk.CTkLabel(self, image=self.user_image, text="")
            self.profile_image_label.place(x=10, y=10)
        except Exception as e:
            print(f"Error loading user image: {e}")
            self.user_image = None

            # Error Label
            self.error_label = ctk.CTkLabel(self, text="Image not found", font=("Arial", 14))
            self.error_label.place(x=10, y=10)

        # Set up the layout
        self.configure(corner_radius=15, width=300, height=200, fg_color="white")

        # Name Label
        self.name_label = ctk.CTkLabel(self, text="Yehah Hacen", font=("Arial", 18, "bold"))
        self.name_label.place(x=100, y=20)

        # Description Label
        self.description_label = ctk.CTkLabel(self, text="Developer", font=("Arial", 14))
        self.description_label.place(x=100, y=50)

        # Contact Label
        self.contact_label = ctk.CTkLabel(self, text="+222 43000038", font=("Arial", 12, "italic"), text_color="gray")
        self.contact_label.place(x=100, y=80)
