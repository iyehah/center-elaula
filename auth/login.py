import customtkinter as ctk
import sqlite3
from ui.dashboard import DashboardWindow
import socket
def is_connected(host="8.8.8.8", port=53, timeout=3):
    """Vérifie la connectivité Internet."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.create_connection((host, port))
        return True
    except OSError:
        return False
class LoginWindow(ctk.CTkFrame):
    def __init__(self, root, go_to_register):
        super().__init__(root)
        self.root = root
        self.go_to_register = go_to_register
        # Vérification de la connexion
        if is_connected():
            label_text = "Connexion Internet disponible"
            label_color = "green"
        else:
            label_text = "Il n'y a pas d'internet"
            label_color = "red"
        # Label for the window
        self.label = ctk.CTkLabel(self, text="Connexion", font=("Arial", 24))
        self.label.pack(pady=10)

        # Entry for student number
        self.number_entry = ctk.CTkEntry(self, placeholder_text="Numéro scolaire", width=450)
        self.number_entry.pack(pady=5)

        # Entry for password
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Mot de passe", show="•", width=450)
        self.password_entry.pack(pady=5)

        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.pack(pady=20, fill="x")

        # Login button
        self.login_button = ctk.CTkButton(self.buttons_frame,fg_color="#4285F4", text="Se connecter", command=self.login)
        self.login_button.pack(pady=10)

        # Account creation button
        self.create_account_button = ctk.CTkButton(self.buttons_frame,text_color="gray", text="Créer un compte", fg_color="transparent",
                                                   border_width=1, border_color="#565b5e", command=self.go_to_register)
        self.create_account_button.pack(pady=10)
        # Création du label avec le message approprié
        label = ctk.CTkLabel(
            root,
            text=label_text,
            text_color=label_color,
            font=("Arial", 12)
        )
        label.pack(pady=0)
    def set_account_exists(self, account_exists):
        """Show or hide the 'Create Account' button based on account existence."""
        if account_exists:
            self.create_account_button.pack_forget()
        else:
            self.create_account_button.pack(pady=10)

    def login(self):
        """Handle login logic."""
        number = self.number_entry.get()
        password = self.password_entry.get()

        # Connect to the database
        conn = sqlite3.connect("./db/school_account.db")
        cursor = conn.cursor()

        # Query to fetch both name and password for the given number
        cursor.execute("SELECT name, password FROM users WHERE number = ?", (number,))
        result = cursor.fetchone()
        conn.close()

        if result and result[1] == password:
            print("Connexion réussie")
            self.result(result[0], result[1])  # Pass the name and password to result
        else:
            print("Identifiants invalides")

    def result(self, name, password):
        """Display the dashboard window."""
        self.root.withdraw()  # Hide the login window

        # Create a new window for the dashboard
        dashboard_window = ctk.CTk()  
        dashboard_window.title(f"{name}")

        # Initialize the dashboard with the user's name and password
        dashboard = DashboardWindow(dashboard_window, name, password)  # Pass name and password
        dashboard.pack(fill="both", expand=True)

        # Start the dashboard window
        dashboard_window.mainloop()