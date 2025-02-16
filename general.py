import customtkinter as ctk
from mainlayout import MainLayout
from topsection import TopSection

class GeneralTab(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)

        # Create the center frame with desired padding and expand options
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.pack(pady=5, padx=5, fill="both", expand=True)

        # Create the TopSection inside the center frame and set it to expand
        self.reports_tab = TopSection(self.center_frame)
        self.reports_tab.pack(fill="both", expand=True)  # Expand to fill both width and height of center_frame

        # Add the MainLayout below the TopSection
        self.main_layout = MainLayout(self.center_frame)
        self.main_layout.pack(fill="both", expand=True, pady=10)  # Add some padding between sections