import customtkinter as ctk
from absent import AbcentReport
from payment import PaymentReport

class ReportsTab(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)
        
        # Main frame for holding reports
        self.center_frame = ctk.CTkFrame(self)
        self.center_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Creating the AbcentReport instance (Attendance Report)
        self.reports_tab = AbcentReport(self.center_frame)
        self.reports_tab.grid(row=0, column=0, padx=50, pady=20, sticky="w")  # Left side

        # Creating the PaymentReport instance (Payment Report)
        self.payment_report_tab = PaymentReport(self.center_frame) 
        self.payment_report_tab.grid(row=0, column=1, padx=20, pady=20, sticky="e")  # Right side

        # Adjust column and row configuration to distribute space
        self.center_frame.grid_columnconfigure(0, weight=1, uniform="equal")  # Left column takes remaining space
        self.center_frame.grid_columnconfigure(1, weight=1, uniform="equal")  # Right column takes remaining space
        self.center_frame.grid_rowconfigure(0, weight=1)
