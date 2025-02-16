import customtkinter as ctk
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib import colors
import datetime
import subprocess
import sys
import os


class CotisationsRaport(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)

        self.root = root

        # Frame for options and buttons
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(pady=10, padx=10, anchor="w")

        # Label for the options frame
        self.options_label = ctk.CTkLabel(self.options_frame, text="Rapport des Enseignants", font=("Arial", 18))
        self.options_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Dropdown for selecting class
        self.class_var = ctk.StringVar(value="Tous")
        class_options = ["Tous", "3As", "4As", "5C", "5D", "6C1", "6C2", "6D", "7C", "7D1", "7D2"]
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

    def fetch_teacher_data(self, selected_class):
        # Connect to the database to fetch teacher data
        conn = sqlite3.connect('teacher_school.db')
        cursor = conn.cursor()

        if selected_class == "Tous":
            cursor.execute("SELECT name, class, subject, salary, number, percentage FROM teachers")
        else:
            cursor.execute("SELECT name, class, subject, salary, number, percentage FROM teachers WHERE class=?", (selected_class,))

        teachers = cursor.fetchall()
        conn.close()
        return teachers

    def generate_report(self):
        selected_class = self.class_var.get()
        teacher_data = self.fetch_teacher_data(selected_class)

        current_date = datetime.datetime.now().strftime('%d/%m/%Y')
        weekday_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        current_weekday = weekday_fr[datetime.datetime.now().weekday()]

        # Create a PDF document
        self.pdf_path = "cotisations_report.pdf"
        pdf = SimpleDocTemplate(self.pdf_path, pagesize=letter, topMargin=5, bottomMargin=5, leftMargin=5, rightMargin=5)
        
        # Fetch school name for the header
        conn = sqlite3.connect('school_account.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users LIMIT 1")
        school_name = cursor.fetchone()[0]
        conn.close()
        
        # Title and header content
        title_text = [
            [school_name],  # Replace with dynamic school name if available
            ["Rapport des Cotisations des Enseignants"],
            [f"Date: {current_date} - {current_weekday}"]
        ]
        title_table = Table(title_text, colWidths=[540])
        title_table.setStyle(TableStyle([ 
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))

        # Table headers
        data = [["Nom", "Classe", "Matière", "Salaire", "Numéro", "Pourcentage", "Statut"]]

        total_price = 0
        total_paid = 0
        total_unpaid_count = 0  # Counter for unpaid teachers
        total_paid_count = 0  # Counter for paid teachers

        # Populate the table with teacher data
        for teacher in teacher_data:
            name, class_, subject, salary, number, percentage = teacher
            status = "Payé" if salary > 0 else "Non payé"
            data.append([name, class_, subject, f"{salary:.2f}", number, f"{percentage}%", status])
            
            total_price += salary
            if salary > 0:
                total_paid += salary
                total_paid_count += 1  # Increment the counter for paid teachers
            else:
                total_unpaid_count += 1  # Increment the counter for unpaid teachers

        # Calculate column widths
        col_widths = [max([len(str(row[i])) for row in data]) * 6 for i in range(len(data[0]))]

        # Create the main table
        main_table = Table(data, colWidths=col_widths)
        main_table.setStyle(TableStyle([ 
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.white]),
        ]))

        # Summary section for the "Résumé des Cotisations"
        summary_data = [
            ["Résumé des Cotisations", "", ""],
            ["Total des prix", "Total Payées (count)", "Total Non Payées (count)"],
            [f"{total_price:.2f}", f"{total_paid_count}", f"{total_unpaid_count}"]
        ]

        # Create the summary table with column headers
        summary_table = Table(summary_data, colWidths=[180, 180, 180])
        summary_table.setStyle(TableStyle([
            ('SPAN', (0, 0), (-1, 0)),  # Span the title row across all columns
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Background color for title row
            ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),  # Background color for header row
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, 1), 12),
            ('FONTSIZE', (0, 2), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 2), (-1, 2), 6)
        ]))

        # Add a spacer between the main table and the summary table
        spacer = Spacer(1, 12)

        # Build PDF with the title, main table, and summary
        pdf.build([title_table, spacer, main_table, spacer, summary_table])

        self.download_button.configure(state="normal")

    def download_pdf(self):
        if self.pdf_path:
            if sys.platform == "win32":
                os.startfile(self.pdf_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.pdf_path])
            else:
                subprocess.Popen(["xdg-open", self.pdf_path])
