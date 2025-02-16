import customtkinter as ctk
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import datetime
import subprocess
import sys
import os

class AbcentReport(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)

        self.root = root

        # Frame for selection and buttons
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(pady=10, padx=10, anchor="w")

        # Label for the options frame
        self.options_label = ctk.CTkLabel(self.options_frame, text="Rapport des absences", font=("Arial", 18))
        self.options_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Dropdown for selecting class (without "All")
        self.class_var = ctk.StringVar(value="3As")  # Default class selected
        class_options = values=["3As", "4As", "5C", "5D", "6C1","6C2", "6D", "7C", "7D1","7D2","P.E","S.C","English","Français"]
        self.class_select = ctk.CTkOptionMenu(self.options_frame, values=class_options, variable=self.class_var)
        self.class_select.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Button to generate the PDF report
        self.generate_button = ctk.CTkButton(self.options_frame, text="Générer PDF", command=self.generate_report)
        self.generate_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # Button to download the PDF
        self.download_button = ctk.CTkButton(self.options_frame, text="Télécharger PDF", command=self.download_pdf)
        self.download_button.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.download_button.configure(state="disabled")  # Initially disabled

        # Store the generated PDF path
        self.pdf_path = None

    def fetch_students(self, selected_class):
        # Connect to the database to fetch student data based on the selected class
        conn = sqlite3.connect('student_school.db')
        cursor = conn.cursor()

        cursor.execute("""SELECT name, parent_number FROM students WHERE class=?""", (selected_class,))
        students = cursor.fetchall()
        conn.close()
        return students

    def generate_report(self):
        selected_class = self.class_var.get()  # Get the selected class
        students = self.fetch_students(selected_class)

        current_date = datetime.datetime.now().strftime('%d/%m/%Y')
        weekday_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        current_weekday = weekday_fr[datetime.datetime.now().weekday()]

        # Create a PDF document
        self.pdf_path = "absence_report.pdf"
        pdf = SimpleDocTemplate(self.pdf_path, pagesize=letter,
                                topMargin=5, bottomMargin=5, leftMargin=5, rightMargin=5)

        # Fetch school name for the header
        conn = sqlite3.connect('school_account.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users LIMIT 1")
        school_name = cursor.fetchone()[0]
        conn.close()

        # Header content (in French)
        title_text = [
            [school_name],
            [f"Formulaire des absences des étudiants - {selected_class}"],  # Include the selected class in the header
            [f"Date: {current_date} - {current_weekday}"]
        ]

        # Define header style
        title_table = Table(title_text, colWidths=[540])
        title_table.setStyle(TableStyle([  
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))

        # Table headers
        data = [["Nom", "Numéro Parent", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]]

        # Add student data to the table (empty cells for days)
        for student in students:
            data.append([student[0], student[1], "", "", "", "", "", ""])

        # Calculate the maximum width for each column (dynamically based on content)
        col_widths = [max([len(str(row[i])) for row in data]) * 6 for i in range(len(data[0]))]
        
        # Create the table with dynamic column widths
        table = Table(data, colWidths=col_widths)

        # Apply style to the table
        table.setStyle(TableStyle([  
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.white])
        ]))

        # Build the PDF with the title and table
        elements = [title_table, table]
        pdf.build(elements)

        # Enable the download button after generating the PDF
        self.download_button.configure(state="normal")

    def download_pdf(self):
        if self.pdf_path:
            if sys.platform == "win32":
                os.startfile(self.pdf_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.pdf_path])
            else:
                subprocess.Popen(["xdg-open", self.pdf_path])

            print("PDF opened.")
