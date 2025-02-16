import customtkinter as ctk
from absent import AbcentReport
from payment import PaymentReport
from cotisations import CotisationsRaport  # Import your new CotisationsRaport class
from financial import FinancialReport

class ReportsTab(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)
         # Configuration de la mise en page du cadre principal
        self.pack(fill="both", expand=True)
        self.grid_rowconfigure(0, weight=0)  # Fixed size for header
        self.grid_rowconfigure(1, weight=1)  # Main content expands
        self.grid_rowconfigure(2, weight=0)  # Fixed size for footer
        self.grid_columnconfigure(0, weight=1)  # Main column expands
        # Main frame for holding reports
        self.center_frame = ctk.CTkFrame(self,fg_color="#CFCFCF")
        self.center_frame.grid(row=0, column=0, pady=10, padx=20, sticky="n")

        # Creating the AbcentReport instance (Attendance Report)
        self.abcent_formulaire = AbcentReport(self.center_frame)
        self.abcent_formulaire.grid(row=0, column=0, padx=10, pady=10)

        # Creating the PaymentReport instance (Payment Report)
        self.payment_report = PaymentReport(self.center_frame) 
        self.payment_report.grid(row=0, column=1, padx=10, pady=10, sticky="e")  # Right side

        # Creating the CotisationsRaport instance (Teacher Contributions Report)
        self.cotisations_report = CotisationsRaport(self.center_frame)
        self.cotisations_report.grid(row=0, column=2, padx=10, pady=10, sticky="e")  # Spans across both columns
        
        # Creating the CotisationsRaport instance (Teacher Contributions Report)
        self.financial_report = FinancialReport(self.center_frame)
        self.financial_report.grid(row=0, column=3, padx=20, pady=20, sticky="e")  # Spans across both columns

        # Adjust column and row configuration to distribute space
        self.center_frame.grid_columnconfigure(0, weight=1, uniform="equal")  # Left column takes remaining space
        self.center_frame.grid_columnconfigure(1, weight=1, uniform="equal")  # Right column takes remaining space
        self.center_frame.grid_rowconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(1, weight=1)  # Add space for the new row
