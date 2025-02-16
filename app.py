import customtkinter as ctk
import sys
import time
from PIL import Image
import sqlite3
from auth.login import LoginWindow
from auth.signin import RegisterWindow

class App:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.geometry("500x400")
        # self.root.overrideredirect(1)  # Hide title bar, including min/max/close buttons
        self.root.resizable(False,False)
        self.root.title("El Mosaeid")

        # Set window icon (optional)
        try:
            self.root.iconbitmap("./img/logo.ico")  # Ensure 'logo.ico' is in the same directory
        except Exception as e:
            print(f"Failed to set icon: {e}")

        # Center the window on the screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 500
        window_height = 350
        position_top = int(screen_height / 2 - window_height / 2)
        position_left = int(screen_width / 2 - window_width / 2)
        self.root.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")

        # Initialize frames
        self.login_frame = LoginWindow(self.root, self.show_register)
        self.register_frame = RegisterWindow(self.root, self.show_login)

        # Database setup
        self.setup_database()

        # Show login frame by default
        self.show_login()
        # Add developer info label
        self.dev_label = ctk.CTkLabel(
            self.root, 
            text="Developer: Iyehah Hacen  |  Contact: 43000038",
            font=("Arial", 9),
            text_color="gray"
        )
        self.dev_label.pack(side="bottom", pady=3)
        

    def setup_database(self):
        """Ensure the database is initialized and check if accounts exist."""
        conn = sqlite3.connect("./db/school_account.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (name TEXT, number TEXT UNIQUE, type TEXT, password TEXT)")
        cursor.execute("SELECT COUNT(*) FROM users")
        account_exists = cursor.fetchone()[0] > 0
        conn.close()

        # Pass account existence status to the login frame
        self.login_frame.set_account_exists(account_exists)

    def show_login(self):
        """Show the login frame and hide the register frame."""
        self.register_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)

    def show_register(self):
        """Show the register frame and hide the login frame."""
        self.login_frame.pack_forget()
        self.register_frame.pack(fill="both", expand=True)

    
    def run(self):
        """Run the application."""
        self.root.mainloop()


def show_loading_screen():
    """Display a loading screen with a logo image."""
    loading = ctk.CTk()
    loading.geometry("300x300")
    loading.overrideredirect(1)  # Hide title bar
    loading.title("Loading...")

    # Center the loading window
    screen_width = loading.winfo_screenwidth()
    screen_height = loading.winfo_screenheight()
    window_width = 300
    window_height = 300
    position_top = int(screen_height / 2 - window_height / 2)
    position_left = int(screen_width / 2 - window_width / 2)
    loading.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")

    # Load and display the logo image
    try:
        logo_image = Image.open("./img/logo.png")  # Ensure 'logo.png' is in the same directory
        logo_image = logo_image.resize((window_width, window_height))
        logo_photo = ctk.CTkImage(logo_image, size=(window_width, window_height))

        logo_label = ctk.CTkLabel(loading, image=logo_photo, text="")
        logo_label.image = logo_photo  # Keep reference to avoid garbage collection
        logo_label.pack(fill="both", expand=True)
    except Exception as e:
        print(f"Failed to load logo image: {e}")

    # Display the loading screen for 2 seconds
    loading.update()
    loading.after(5000, loading.destroy)
    loading.mainloop()


if __name__ == "__main__":
    # Show loading screen
    show_loading_screen()

    # Run the application
    App().run()
