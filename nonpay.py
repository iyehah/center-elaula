import customtkinter as ctk
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib import colors
import datetime
import subprocess
import sys
import os

class ClassNonPay(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)

        self.root = root

        # Frame for selection and buttons
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(pady=10, padx=10, anchor="w")

        # Label for the options frame
        self.options_label = ctk.CTkLabel(self.options_frame, text="R.étudiants non payés", font=("Arial", 12))
        self.options_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Dropdown for selecting class (optional for payment report)
        self.class_var = ctk.StringVar(value="Tous")
        class_options = self.get_classes_from_db()
        self.class_select = ctk.CTkOptionMenu(self.options_frame, values=["Tous"] + class_options, variable=self.class_var)
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

    def get_classes_from_db(self):
        # Retrieve the list of classes from the database
        conn = sqlite3.connect('./db/student_school.db')
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT class FROM students")
        classes = [row[0] for row in cursor.fetchall()]
        conn.close()
        return classes

    def fetch_non_pay_data(self, selected_class=None):
        # Fetch non-paid student data based on the selected class
        conn = sqlite3.connect('./db/student_school.db')
        cursor = conn.cursor()

        if selected_class == "Tous":
            cursor.execute("""
                SELECT name, subject, date_register, parent_number, price, date_pay, class
                FROM students WHERE price = 0
                ORDER BY class
            """)
        else:
            cursor.execute("""
                SELECT name, subject, date_register, parent_number, price, date_pay
                FROM students WHERE class = ? AND price = 0
            """, (selected_class,))

        students = cursor.fetchall()
        conn.close()
        return students

    def generate_report(self):
        selected_class = self.class_var.get()
        data_by_class = {}

        if selected_class == "Tous":
            # Group data by class
            all_data = self.fetch_non_pay_data("Tous")
            for student in all_data:
                student_class = student[6]
                if student_class not in data_by_class:
                    data_by_class[student_class] = []
                data_by_class[student_class].append(student)
        else:
            data_by_class[selected_class] = self.fetch_non_pay_data(selected_class)

        current_date = datetime.datetime.now().strftime('%d/%m/%Y')
        weekday_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        current_weekday = weekday_fr[datetime.datetime.now().weekday()]

        # Create a PDF document
        self.pdf_path = "non_pay_report.pdf"
        pdf = SimpleDocTemplate(self.pdf_path, pagesize=letter,
                                topMargin=5, bottomMargin=5, leftMargin=5, rightMargin=5)

        # Fetch school name for the header
        conn = sqlite3.connect('./db/school_account.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users LIMIT 1")
        school_name = cursor.fetchone()[0]
        conn.close()

        elements = []

        # Header content
        title_text = [
            [school_name],
            ["Rapport des étudiants non payés"],
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
        elements.append(title_table)
        elements.append(Spacer(1, 12))

        # Generate table for each class
        for class_name, students in data_by_class.items():
            # Add class title
            class_title = [[f"Classe : {class_name}"]]
            class_title_table = Table(class_title, colWidths=[540])
            class_title_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ]))
            elements.append(class_title_table)
            elements.append(Spacer(1, 6))

            # Add student data table
            data = [["Nom", "Matière", "Date Inscription", "Numéro Parent", "Prix", "Date Paiement"]]
            for student in students:
                data.append([student[0], student[1], student[2], student[3], student[4], student[5]])

            col_widths = [max(len(str(row[i])) for row in data) * 6 for i in range(len(data[0]))]
            table = Table(data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))

        # Build the PDF
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

            print("PDF ouvert.")
