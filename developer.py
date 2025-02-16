import customtkinter as ctk
from tkinter import PhotoImage
from PIL import Image, ImageTk

class DeveloperTab(ctk.CTkFrame):
    def __init__(self, root, image_path="./dev.png", name="Yehah Hacen", description="Developer", contact="+222 43000038"):
        super().__init__(root)
        
        self.image_path = image_path
        self.name = name
        self.description = description
        self.contact = contact

        self.setup_ui()

    def setup_ui(self):
        # Load images safely
        try:
            # Convert image to PhotoImage using PIL
            pil_image = Image.open(self.image_path).resize((80, 80), Image.Resampling.LANCZOS)
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
        self.name_label = ctk.CTkLabel(self, text=self.name, font=("Arial", 18, "bold"))
        self.name_label.place(x=100, y=20)

        # Description Label
        self.description_label = ctk.CTkLabel(self, text=self.description, font=("Arial", 14))
        self.description_label.place(x=100, y=50)

        # Contact Label
        self.contact_label = ctk.CTkLabel(self, text=self.contact, font=("Arial", 12, "italic"), text_color="gray")
        self.contact_label.place(x=100, y=80)

        # Close Button
        self.close_button = ctk.CTkButton(self, text="Close", command=self.close_window)
        self.close_button.place(x=100, y=120)

    def close_window(self):
        """Close the developer window."""
        self.master.destroy()
