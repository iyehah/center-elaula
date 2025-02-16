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

class FinancialReport(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)

        self.root = root

        # Frame for selection and buttons
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(pady=10, padx=10, anchor="w")

        # Label for the options frame
        self.options_label = ctk.CTkLabel(self.options_frame, text="Rapports financiers", font=("Arial", 12))
        self.options_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Button to generate the PDF report
        self.generate_button = ctk.CTkButton(self.options_frame, text="Générer PDF", command=self.generate_report)
        self.generate_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Button to download the PDF
        self.download_button = ctk.CTkButton(self.options_frame, text="Télécharger PDF", command=self.download_pdf)
        self.download_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.download_button.configure(state="disabled")  # Initially disabled

        # Store the generated PDF path
        self.pdf_path = None

    def fetch_financial_data(self):
        # Connect to the databases and fetch data
        total_revenue = 0
        total_debt = 0
        total_salaries = 0
        total_costs = 0

        # Fetch total revenue and debt from student_school.db
        conn_students = sqlite3.connect('./db/student_school.db')
        cursor_students = conn_students.cursor()
        cursor_students.execute("SELECT SUM(price), SUM(discount) FROM students")
        student_data = cursor_students.fetchone()
        if student_data:
            total_revenue = student_data[0] or 0
            total_debt = student_data[1] or 0
        conn_students.close()

        # Fetch total salaries from teacher_school.db
        conn_teachers = sqlite3.connect('./db/teacher_school.db')
        cursor_teachers = conn_teachers.cursor()
        cursor_teachers.execute("SELECT SUM(salary) FROM teachers")
        teacher_data = cursor_teachers.fetchone()
        if teacher_data:
            total_salaries = teacher_data[0] or 0
        conn_teachers.close()

        # Fetch total costs from costs_school.db
        conn_costs = sqlite3.connect('./db/costs_school.db')
        cursor_costs = conn_costs.cursor()
        cursor_costs.execute("SELECT SUM(costs) FROM costs")
        cost_data = cursor_costs.fetchone()
        if cost_data:
            total_costs = cost_data[0] or 0
        conn_costs.close()

        total_charges = total_salaries + total_costs
        remaining_revenue = total_revenue - total_charges

        return total_revenue, total_debt, total_salaries, total_costs, total_charges, remaining_revenue

    def generate_report(self):
        financial_data = self.fetch_financial_data()
        total_revenue, total_debt, total_salaries, total_costs, total_charges, remaining_revenue = financial_data

        current_date = datetime.datetime.now().strftime('%d/%m/%Y')
        weekday_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        current_weekday = weekday_fr[datetime.datetime.now().weekday()]

        # Create a PDF document
        self.pdf_path = "financial_report.pdf"
        pdf = SimpleDocTemplate(self.pdf_path, pagesize=letter,
                                topMargin=5, bottomMargin=5, leftMargin=5, rightMargin=5)
        # Fetch school name for the header
        conn = sqlite3.connect('./db/school_account.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users LIMIT 1")
        school_name = cursor.fetchone()[0]
        conn.close()
        # Header content (in French)
        title_text = [
            [school_name],
            ["Rapports financiers"],
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

        # Financial summary data
        data = [
            ["Détails", "Montant (DA)"],
            ["Total Revenu", total_revenue],
            ["Total Dette", total_debt],
            ["Total Salaires", total_salaries],
            ["Total des Coûts", total_costs],
            ["Total des Charges", total_charges],
            ["Revenu Restant", remaining_revenue]
        ]

        # Create the table
        main_table = Table(data, colWidths=[300, 240])
        main_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        # Build the PDF
        elements = [title_table, Spacer(1, 12), main_table]
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
