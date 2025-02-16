import customtkinter as ctk
import subprocess
import sys
from general import GeneralTab  # Assuming GeneralTab is defined in general.py
from student import StudentTab  # Assuming StudentTab is defined in student.py
from teacher import TeacherTab  # Assuming TeacherTab is defined in teacher.py
from statistic import StatisticsTab  # Assuming StatisticsTab is defined in statistic.py
from contable import ContableTab  # Assuming ContableTab is defined in contable.py
from registerabcent import RegisterAbcentTab  # Assuming this is defined
from reports import ReportsTab  # Assuming this is defined
# from developer import Developer  # Assuming this is defined in developer.py


class DashboardWindow(ctk.CTkFrame):
    def __init__(self, root, name, password):
        super().__init__(root)
        self.root = root
        self.name = name
        self.password = password

        # Set window icon
        try:
            self.root.iconbitmap("logo.ico")  # Replace with the correct path to your .ico file
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
            self, text="Reload", width=50, command=self.reload_dashboard,state="disabled"
        )
        self.reload_button.place(relx=0.9, rely=0.05, anchor="ne")

        # Add a logout button at the bottom-right
        self.exit_button = ctk.CTkButton(self, text="Déconnexion", width=50, command=self.logout)
        self.exit_button.place(relx=0.99, rely=0.05, anchor="ne")

    def add_tabs(self):
        """Add all tabs to the TabView."""
        # General Tab
        self.tabview.add("Général")
        general_tab = GeneralTab(self.tabview.tab("Général"))
        general_tab.pack(expand=True, fill="both")

        # Student Tab
        self.tabview.add("Étudiant")
        student_tab = StudentTab(self.tabview.tab("Étudiant"))
        student_tab.pack(expand=True, fill="both")

        # Teacher Tab
        self.tabview.add("Enseignant")
        teacher_tab = TeacherTab(self.tabview.tab("Enseignant"))
        teacher_tab.pack(expand=True, fill="both")

        # Contable Tab
        self.tabview.add("Comptable")
        contable_tab = ContableTab(self.tabview.tab("Comptable"))
        contable_tab.pack(expand=True, fill="both")

        # Register Absent Tab
        self.tabview.add("Informer l'agent")
        registerabcent_tab = RegisterAbcentTab(self.tabview.tab("Informer l'agent"))
        registerabcent_tab.pack(expand=True, fill="both")

        # Statistics Tab
        self.tabview.add("Statistiques")
        statistics_tab = StatisticsTab(self.tabview.tab("Statistiques"))
        statistics_tab.pack(expand=True, fill="both")

        # Reports Tab
        self.tabview.add("Formulaire & Rapports")
        reports_tab = ReportsTab(self.tabview.tab("Formulaire & Rapports"))
        reports_tab.pack(expand=True, fill="both")

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
