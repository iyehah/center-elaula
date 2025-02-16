import customtkinter as ctk
import subprocess
import sys
import socket
from pathlib import Path
from mod.general import GeneralTab
from mod.student import StudentTab
from mod.teacher import TeacherTab
from mod.statistic import StatisticsTab
from mod.contable import ContableTab
from mod.reports import ReportsTab
from developer import DeveloperTab

# Check internet connectivity before importing `RegisterAbcentTab`
def is_connected(host="8.8.8.8", port=53, timeout=3):
    """Check internet connectivity."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.create_connection((host, port))
        return True
    except OSError:
        return False

# Conditional import based on connectivity
try:
    if is_connected():
        from mod.registerabcent import RegisterAbcentTab
except ImportError:
    RegisterAbcentTab = None

class DashboardWindow(ctk.CTkFrame):
    def __init__(self, root, name, password):
        super().__init__(root)
        self.root = root
        self.name = name
        self.password = password

        # Set window icon
        icon_path = Path("./img/logo.ico")
        if icon_path.exists():
            try:
                self.root.iconbitmap(icon_path)
            except Exception as e:
                print(f"Error loading icon: {e}")

        # Configure window size and behavior
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.maxsize(screen_width, screen_height)
        self.root.minsize(800, 500)
        self.root.resizable(True, True)

        # Welcome Label
        self.label = ctk.CTkLabel(self, text=f"Bienvenue, {self.name}", font=("Arial", 24))
        self.label.pack(pady=10)

        # Create TabView for sections
        self.tabview = ctk.CTkTabview(self, fg_color="#DBDBDB")
        self.tabview.pack(expand=True, fill="both", pady=10)

        # Add main tabs
        self.add_tabs()

        # Add a reload button at the top-right
        self.reload_button = ctk.CTkButton(
            self, text="Reload", width=50, command=self.reload_dashboard, state="disabled"
        )
        self.reload_button.place(relx=0.9, rely=0.05, anchor="ne")

        # Add a logout button at the bottom-right
        self.exit_button = ctk.CTkButton(self, text="Déconnexion", width=50, command=self.logout)
        self.exit_button.place(relx=0.99, rely=0.05, anchor="ne")

    def add_tabs(self):
        """Add all tabs to the TabView."""
        tabs = [
            ("Général", GeneralTab),
            ("Étudiant", StudentTab),
            ("Enseignant", TeacherTab),
            ("Comptable", ContableTab),
            ("Statistiques", StatisticsTab),
            ("Formulaire & Rapports", ReportsTab)
            # ("Développeur", DeveloperTab)
        ]

        for tab_name, tab_class in tabs:
            self.tabview.add(tab_name)
            tab_instance = tab_class(self.tabview.tab(tab_name))
            tab_instance.pack(expand=True, fill="both")

        if is_connected():
            self.tabview.add("Informer l'agent")
            registerabcent_tab = RegisterAbcentTab(self.tabview.tab("Informer l'agent"))
            registerabcent_tab.pack(expand=True, fill="both")
        else:
            print("No internet connection. 'Informer l'agent' tab is not loaded.")

    def reload_dashboard(self):
        """Reload all tabs in the dashboard."""
        print("Reloading dashboard...")
        self.tabview.destroy()  # Remove the current TabView
        self.tabview = ctk.CTkTabview(self, fg_color="#DBDBDB")  # Recreate TabView
        self.tabview.pack(expand=True, fill="both", pady=10)
        self.add_tabs()  # Re-add all tabs

    def logout(self):
        """Log out and restart the application."""
        print("Déconnexion...")

        # Relaunch app.py
        try:
            subprocess.Popen([sys.executable, "app.py"])
        except Exception as e:
            print(f"Error relaunching app: {e}")

        sys.exit()
