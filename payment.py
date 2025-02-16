import customtkinter as ctk
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import datetime
import subprocess
import sys
import os
from reportlab.platypus import Spacer

class PaymentReport(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)

        self.root = root

        # Frame for selection and buttons
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(pady=10, padx=10, anchor="w")

        # Label for the options frame
        self.options_label = ctk.CTkLabel(self.options_frame, text="Rapport des paiements", font=("Arial", 18))
        self.options_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Dropdown for selecting class (optional for payment report)
        self.class_var = ctk.StringVar(value="Tous")
        class_options = values=["Tous", "3As", "4As", "5C", "5D", "6C1","6C2", "6D", "7C", "7D1","7D2","P.E","S.C","English","Français"]
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

    def fetch_payment_data(self, selected_class):
        # Connect to the database to fetch student payment data
        conn = sqlite3.connect('student_school.db')
        cursor = conn.cursor()

        if selected_class == "Tous":
            cursor.execute("""
                SELECT name, subject, date_register, parent_number, price, date_pay 
                FROM students
            """)
        else:
            cursor.execute("""
                SELECT name, subject, date_register, parent_number, price, date_pay 
                FROM students WHERE class=?
            """, (selected_class,))

        students = cursor.fetchall()
        conn.close()
        return students

    def generate_report(self):
        selected_class = self.class_var.get()
        payment_data = self.fetch_payment_data(selected_class)

        current_date = datetime.datetime.now().strftime('%d/%m/%Y')
        weekday_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        current_weekday = weekday_fr[datetime.datetime.now().weekday()]

        # Create a PDF document
        self.pdf_path = "payment_report.pdf"
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
            ["Rapport de paiements des étudiants"],
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
        data = [["Nom", "Matière", "Date Inscription", "Numéro Parent", "Prix", "Date Paiement", "Statut"]]

        # Add payment data to the table
        total_price = 0
        total_paid = 0
        total_unpaid = 0

        for student in payment_data:
            price = student[4]  # Price field from the database
            status = "Payée" if price > 0 else "Non Payée"
            data.append([student[0], student[1], student[2], student[3], student[4], student[5], status])

            # Update totals
            total_price += price
            if price > 0:
                total_paid += 1
            else:
                total_unpaid += 1

        # Calculate the maximum width for each column
        col_widths = [max([len(str(row[i])) for row in data]) * 6 for i in range(len(data[0]))]

        # Create the main table with dynamic column widths
        main_table = Table(data, colWidths=col_widths)

        # Apply style to the main table
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

        # Summary section below the main table
        summary_data = [
            ["Résumé des paiements", "", ""],
            ["Total des prix", "Total Payées", "Total Non Payées"],
            [f"{total_price}", f"{total_paid}", f"{total_unpaid}"]
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
        spacer = Spacer(1, 12)  # Adjust the 12 to the desired amount of space (in points)

        # Build the PDF with the title, main table, and summary
        elements = [title_table, main_table, spacer, summary_table]
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