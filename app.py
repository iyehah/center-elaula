import customtkinter as ctk
import sys
import time
from PIL import Image
import sqlite3
from login import LoginWindow
from signin import RegisterWindow

class App:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.geometry("500x400")
        self.root.overrideredirect(1)  # Hide title bar, including min/max/close buttons
        self.root.title("School Management App")

        # Set window icon (optional, if you have an .ico file)
        try:
            self.root.iconbitmap("logo.ico")  # Ensure 'logo.ico' is in the same directory as this script
        except Exception as e:
            print(f"Failed to set icon: {e}")

        # Center the window on the screen and make it non-resizable
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 500
        window_height = 350
        position_top = int(screen_height / 2 - window_height / 2)
        position_left = int(screen_width / 2 - window_width / 2)
        self.root.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")

        # Initialize both frames
        self.login_frame = LoginWindow(self.root, self.show_register)
        self.register_frame = RegisterWindow(self.root, self.show_login)

        # Check if any accounts exist in the database and hide the "Create Account" button if needed
        conn = sqlite3.connect("school_account.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (name TEXT, number TEXT UNIQUE, type TEXT, password TEXT)")
        cursor.execute("SELECT COUNT(*) FROM users")
        account_exists = cursor.fetchone()[0] > 0
        conn.close()

        # Pass the account existence status to the login frame
        self.login_frame.set_account_exists(account_exists)

        # Show the login frame by default
        self.show_login()

        # Exit App Button (Add this to quit the app and re-run app.py)
        self.exit_button = ctk.CTkButton(self.root, text="Exit App", width=50, command=self.exit_app)
        self.exit_button.pack(side="bottom", pady=10)

    def show_login(self):
        """Show the login frame and hide the register frame."""
        self.register_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)

    def show_register(self):
        """Show the register frame and hide the login frame."""
        self.login_frame.pack_forget()
        self.register_frame.pack(fill="both", expand=True)

    def exit_app(self):        
        # Close the Tkinter window and quit the app
        self.root.quit()
        self.root.destroy()
        # Exit the current Python process
        sys.exit()

    def run(self):
        self.root.mainloop()

def show_loading_screen():
    """Display a loading screen with an image for 5 seconds."""
    loading = ctk.CTk()
    loading.geometry("300x300")
    loading.overrideredirect(1)  # Hide the title bar
    loading.title("Loading...")

    # Center the loading window on the screen
    screen_width = loading.winfo_screenwidth()
    screen_height = loading.winfo_screenheight()
    window_width = 300
    window_height = 300
    position_top = int(screen_height / 2 - window_height / 2)
    position_left = int(screen_width / 2 - window_width / 2)
    loading.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")

    # Load and display the image
    try:
        logo_image = Image.open("logo.png")  # Ensure 'logo.png' is in the same directory
        # Resize the image to fill the entire window size
        logo_image = logo_image.resize((window_width, window_height))
        
        # Convert the PIL Image to a CTkImage
        logo_photo = ctk.CTkImage(logo_image, size=(window_width, window_height))

        # Display the image in the loading window
        logo_label = ctk.CTkLabel(loading, image=logo_photo, text="")
        logo_label.image = logo_photo  # Keep a reference to avoid garbage collection
        logo_label.pack(fill="both", expand=True)  # Make sure the label expands to fill the window

    except Exception as e:
        print(f"Failed to load logo image: {e}")

    # Keep the loading screen open for 5 seconds
    loading.update()
    loading.after(5000, loading.destroy)  # Destroy the loading screen after 5 seconds
    loading.mainloop()

if __name__ == "__main__":
    # Show loading screen for 5 seconds
    show_loading_screen()
    # Start the main application
    App().run()
