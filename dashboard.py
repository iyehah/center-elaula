import customtkinter as ctk
import subprocess
import sys
from student import StudentTab  # Assuming you have the StudentTab defined in student.py
from teacher import TeacherTab  # Assuming you have the TeacherTab defined in teacher.py
from statistic import StatisticsTab  # Assuming you have the StatisticsTab defined in statistic.py
from reports import ReportsTab  # Assuming you have the ReportsTab defined in reports.py
from setting import SettingsTab  # Assuming you have the SettingsTab defined in setting.py

class DashboardWindow(ctk.CTkFrame):
    def __init__(self, root, name, password):
        super().__init__(root)
        self.root = root
        self.name = name
        self.password = password

        # Set the window icon
        self.root.iconbitmap("logo.ico")  # Replace with the correct path to your .ico file

        # Maximize the window
        self.root.state('zoomed')

        # Welcome Label
        self.label = ctk.CTkLabel(self, text=f"Bienvenue, {self.name}", font=("Arial", 24))
        self.label.pack(pady=10)

        # Create a Tabview for dashboard sections
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", pady=10)

        # Add main tabs
        self.tabview.add("Étudiant")
        self.tabview.add("Enseignant")
        self.tabview.add("Statistiques")
        self.tabview.add("Rapports")  # Added Reports tab
        self.tabview.add("Paramètres")  # Added Settings tab

        # Add StudentTab to the "Étudiant" tab
        student_tab = StudentTab(self.tabview.tab("Étudiant"))
        student_tab.pack(expand=True, fill="both")

        # Add TeacherTab to the "Enseignant" tab
        teacher_tab = TeacherTab(self.tabview.tab("Enseignant"))
        teacher_tab.pack(expand=True, fill="both")

        # Add StatisticsTab to the "Statistiques" tab
        statistics_tab = StatisticsTab(self.tabview.tab("Statistiques"))
        statistics_tab.pack(expand=True, fill="both")

        # Add ReportsTab to the "Rapports" tab
        reports_tab = ReportsTab(self.tabview.tab("Rapports"))
        reports_tab.pack(expand=True, fill="both")

        # Add SettingsTab to the "Paramètres" tab
        settings_tab = SettingsTab(self.tabview.tab("Paramètres"))  # Pass name and password to SettingsTab
        settings_tab.pack(expand=True, fill="both")

        # Add Logout button (placed at the bottom-right corner)
        self.exit_button = ctk.CTkButton(self, text="Déconnexion", command=self.logout)
        self.exit_button.place(relx=0.95, rely=0.95, anchor="se")

    def logout(self):
        """Exit the current application and relaunch app.py."""
        print("Déconnexion...")

        # Close the Tkinter window and quit the application
        self.root.quit()
        self.root.destroy()

        # Relaunch app.py using subprocess
        subprocess.Popen([sys.executable, "app.py"])

        # Exit the current Python process
        sys.exit()
