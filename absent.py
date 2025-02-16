import customtkinter as ctk
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle ,Image,Spacer
from reportlab.lib.pagesizes import A4  # Standard A4 page size
from reportlab.lib.units import inch  # For unit measurements in PDF
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
        self.options_label = ctk.CTkLabel(self.options_frame, text="Formulaire des absences", font=("Arial", 12))
        self.options_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Dropdown for selecting class
        self.class_var = ctk.StringVar(value="3As")  # Default class selected
        class_options = ["3As", "4As", "5C", "5D", "6C1", "6C2", "6D", "7C", "7D1", "7D2", "P.E", "S.C", "English", "Français"]
        self.class_select = ctk.CTkOptionMenu(self.options_frame, values=class_options, variable=self.class_var)
        self.class_select.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Button to generate the PDF report
        self.generate_button = ctk.CTkButton(self.options_frame, text="Générer PDF", command=self.generate_report)
        self.generate_button.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        # Button to download the PDF
        self.download_button = ctk.CTkButton(self.options_frame, text="Télécharger PDF", command=self.download_pdf)
        self.download_button.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.download_button.configure(state="disabled")  # Initially disabled

        # Store the generated PDF path
        self.pdf_path = None

    def fetch_students(self, selected_class):
        conn = sqlite3.connect('./db/student_school.db')
        cursor = conn.cursor()
        cursor.execute("""SELECT name, subject FROM students WHERE class=?""", (selected_class,))
        students = cursor.fetchall()
        conn.close()
        return students

    def generate_report(self):
        selected_class = self.class_var.get()  # Classe sélectionnée
        students = self.fetch_students(selected_class)

        current_date = datetime.datetime.now().strftime('%d/%m/%Y')
        weekday_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        current_weekday = weekday_fr[datetime.datetime.now().weekday()]

        # Création d'un document PDF
        self.pdf_path = "absence_report.pdf"
        pdf = SimpleDocTemplate(self.pdf_path, pagesize=letter,
                                topMargin=0, bottomMargin=0, leftMargin=0, rightMargin=0)
        # Ajouter un logo (si disponible)
        logo_path = "./img/header.jpg"  # Assurez-vous que ce fichier existe
        if os.path.exists(logo_path):
            logo = Image(logo_path)
            logo.drawHeight = 1 * inch
            logo.drawWidth = A4[0]  # Largeur complète de la page
            logo.hAlign = 'CENTER'
            # elements.append(logo)

        # Ajouter un titre "Reçu"
        # pdf.append(Spacer(1, 20))

        # Entête du tableau
        title_text = [
            [f"Formulaire des absences des étudiants - {selected_class}"],
            [f"Date: {current_date} - {current_weekday}"]
        ]
        title_table = Table(title_text, colWidths=[540])
        title_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))

        # Jours sélectionnés (par exemple, Lundi, Mardi, etc.)
        selected_days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
        
        # En-têtes du tableau
        headers = ["Nom et Pénom", "Matières"] + selected_days
        data = [headers]

        # Corps du tableau
        for student in students:
            row = [student[0], student[1]]  # Ajouter le nom et numéro parent
            row.extend([""] * len(selected_days))  # Ajouter des cellules vides pour les jours
            data.append(row)

        # Largeur des colonnes
        col_widths = [120, 120] + [60] * len(selected_days)

        # Création du tableau
        table = Table(data, colWidths=col_widths)

        # Style du tableau
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Couleur d'arrière-plan des en-têtes
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Couleur du texte des en-têtes
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Aligner le texte au centre
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Police des en-têtes
            ('FONTSIZE', (0, 0), (-1, 0), 10),  # Taille de police des en-têtes
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),  # Espacement des en-têtes
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Grille noire
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.white])  # Fond des lignes
        ]))

        # Création du PDF
        elements = [logo,title_table, table]
        pdf.build(elements)

        self.download_button.configure(state="normal")



    def download_pdf(self):
        if self.pdf_path:
            if sys.platform == "win32":
                os.startfile(self.pdf_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.pdf_path])
            else:
                subprocess.Popen(["xdg-open", self.pdf_path])
