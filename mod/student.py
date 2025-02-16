import customtkinter as ctk  # For the GUI framework
import sqlite3  # For database operations
from datetime import datetime  # To get the current date and time
from tkcalendar import DateEntry  # For date picker widget
from tkinter import messagebox, simpledialog  # For user dialogs in tkinter
import os  # For file and directory operations
import qrcode  # For QR code generation
from reportlab.pdfgen import canvas  # For creating PDFs
from reportlab.lib.pagesizes import A4  # Standard A4 page size
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image  # For PDF layout and elements
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # For text styles in PDFs
from reportlab.lib.enums import TA_RIGHT, TA_CENTER  # Text alignment options
from reportlab.pdfbase.ttfonts import TTFont  # For custom font registration
from reportlab.pdfbase import pdfmetrics  # For managing fonts
from reportlab.lib.units import inch  # For unit measurements in PDF
from reportlab.lib import colors  # For color definitions
from bidi.algorithm import get_display  # For bidirectional text support
import arabic_reshaper  # To reshape Arabic text for proper rendering
import socket  # To check internet connectivity


def is_connected(host="8.8.8.8", port=53, timeout=3):
    """Check internet connectivity."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.create_connection((host, port))
        return True
    except OSError:
        return False

# Conditional import based on connectivity
if is_connected():
    import pywhatkit


class StudentTab(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)
        
        # Connexion à la base de données et création de la table des étudiants si elle n'existe pas
        self.conn = sqlite3.connect("./db/student_school.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                                id INTEGER PRIMARY KEY,
                                name TEXT,
                                gender TEXT,
                                class TEXT,
                                subject TEXT,
                                date_register TEXT,
                                parent_number TEXT,
                                price REAL,
                                date_pay TEXT,
                                discount REAL
                            )''')
        self.conn.commit()

        # Cadre de recherche et filtre
        self.search_frame = ctk.CTkFrame(self,fg_color="#DBDBDB")
        self.search_frame.grid(row=0, column=0, padx=10, pady=10, columnspan=2, sticky="nsew")
        
        # Champ de recherche
        self.search_entry = ctk.CTkEntry(self.search_frame,width=300, placeholder_text="Rechercher par nom")
        self.search_entry.grid(row=0, column=0, padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", self.filter_students)
        
        # Filtre par classe
        self.class_filter = ctk.CTkOptionMenu(self.search_frame,fg_color="white",button_color="#4285F4",dropdown_fg_color="white",dropdown_hover_color="#4285F4",text_color="black",width=200, values=["Tous", "3As", "4As", "5C", "5D", "6C1","6C2", "6D", "7C", "7D1","7D2","P.E","S.C","English","Français"])
        self.class_filter.set("Tous")
        self.class_filter.grid(row=0, column=1, padx=5, pady=5)
        self.class_filter.bind("<<ComboboxSelected>>", self.filter_students)
        
        # "Filtre par classe" button
        self.filter_button = ctk.CTkButton(self.search_frame,fg_color="#4285F4", text="Filtrer par classe", command=self.filter_students)
        self.filter_button.grid(row=0, column=2, padx=5, pady=5)
        
        
        # Date filters using tkcalendar DateEntry
        self.date_pay_entry = DateEntry(
            self.search_frame,
            width=15,
            height=1,
            relief="solid",
            border=3,
            popup_background="gray",
            background="#4285F4",   # Background color for the DateEntry itself
            foreground="white",       # Text color
            borderwidth=2,            # Border width around the DateEntry widget
            date_pattern='yyyy-mm-dd',  # Format for the date
            font=("Arial", 12),        # Font for the text inside the DateEntry
            padding=(5, 5)            # Padding inside the widget to adjust the space between the border and text
        )
        # Set the initial date to empty
        self.date_pay_entry.grid(row=0, column=3, padx=5, pady=5)

        # "Filtrer par date de paiement" button
        self.filter_by_pay_button = ctk.CTkButton(self.search_frame,fg_color="#4285F4",text="Filtrer par paiement", command=self.filter_students)
        self.filter_by_pay_button.grid(row=0, column=4, padx=5, pady=5)
        
        

        # Cadre de la table des étudiants
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Configurer les colonnes pour occuper 80% de la fenêtre
        self.grid_columnconfigure(0, weight=1)  # Cela permettra à la table d'occuper 80% de la largeur de la fenêtre
        
        # Créer un cadre défilant pour le contenu de la table
        self.scrollable_frame = ctk.CTkScrollableFrame(self.table_frame, width=1000, height=700,fg_color="#CFCFCF")
        self.scrollable_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # En-têtes de table
        self.headers = ["Nom", "Genre", "Classe", "Matière", "Date d'inscription", "Numéro des parents", "Prix", "Date de paiement", "Dette due", "Actions"]
        
        # Configurer les colonnes pour prendre un espace égal
        num_columns = len(self.headers)
        for col in range(num_columns):
            self.scrollable_frame.grid_columnconfigure(col, weight=1)
        
        # Ajouter les labels d'en-tête
        for col, header in enumerate(self.headers):
            header_label = ctk.CTkLabel(self.scrollable_frame, text=header, font=("Arial", 12, "bold"), padx=5, pady=5, text_color="white", fg_color="#4285F4")
            header_label.grid(row=0, column=col, sticky="nsew")

        # Label en bas pour afficher le nombre d'étudiants 
        self.count_label = ctk.CTkLabel(self.table_frame,width=200,corner_radius=12, fg_color="#4285F4",text_color="white", text="Total des étudiants : 0", font=("Arial", 12))
        self.count_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.price_label = ctk.CTkLabel(self.table_frame,width=200,corner_radius=12, fg_color="#4285F4",text_color="white", text="Total Prix : 0", font=("Arial", 12))
        self.price_label.grid(row=1, column=0, padx=20, pady=10, sticky="")

        self.discount_label = ctk.CTkLabel(self.table_frame,width=200,corner_radius=12, fg_color="#4285F4",text_color="white", text="Total Dette : 0", font=("Arial", 12))
        self.discount_label.grid(row=1, column=0, padx=40, pady=10, sticky="e")


        # Cadre du formulaire d'ajout/édition d'étudiant
        self.add_student_form = AddStudentForm(self)
        self.add_student_form.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        
        
        # Display all students initially
        self.display_students()
    def display_students(self, filter_name="", filter_class="Tous", filter_date_pay=""):
        """Retrieve and display student records based on filters."""
        for widget in self.scrollable_frame.winfo_children():
            if int(widget.grid_info()["row"]) > 0:  # Skip headers
                widget.destroy()

        query = "SELECT id, name, gender, class, subject, date_register, parent_number, price, date_pay, discount FROM students WHERE 1=1"
        params = []
        
        if filter_name:
            query += " AND name LIKE ?"
            params.append(f"%{filter_name}%")
        
        if filter_class != "Tous":
            query += " AND class = ?"
            params.append(filter_class)
        
        if filter_date_pay:
            query += " AND date_pay = ?"
            params.append(filter_date_pay)

        total_price = 0  # Initialize total price
        total_discount = 0  # Initialize total discount
        
        self.cursor.execute(query, params)
        students = self.cursor.fetchall()

        for row, student in enumerate(students, start=1):
            student_id, *student_data = student
            for col, data in enumerate(student_data):
                cell = ctk.CTkLabel(self.scrollable_frame, text=data, padx=5, pady=5)
                cell.grid(row=row, column=col, sticky="nsew")
            
            price = student[7]
            discount = student[9]
            total_price += price
            total_discount += discount

            # Determine the state of the button based on the condition
            button_state = "normal" if price > 0 and discount == 0 else "disabled"
            actions_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            actions_frame.grid(row=row, column=len(self.headers)-1, padx=5, pady=5, sticky="nsew")
            print_button = ctk.CTkButton(
                actions_frame, 
                text="Print",
                fg_color="#4285F4", 
                width=50,
                state=button_state,  
                command=lambda sid=student_id: self.print_student(sid)
                )
            print_button.pack(side="left", expand=True, padx=5, pady=5)

            edit_button = ctk.CTkButton(actions_frame, text="Modifier",fg_color="#4285F4", width=50, command=lambda sid=student_id: self.edit_student(sid))
            edit_button.pack(side="left", expand=True, padx=5, pady=5)

            delete_button = ctk.CTkButton(actions_frame, text="Supprimer",fg_color="#4285F4", width=60, command=lambda sid=student_id: self.delete_student(sid))
            delete_button.pack(side="left", expand=True, padx=5, pady=5)

        # Update labels with the total count, price, and discount
        self.count_label.configure(text=f"Total des étudiants : {len(students)}")
        self.price_label.configure(text=f"Total Prix : {total_price}")
        self.discount_label.configure(text=f"Total Dette : {total_discount}")
    def filter_students(self, event=None):
        """Filter students based on search text, class filter, and date filters."""
        search_text = self.search_entry.get().strip()
        selected_class = self.class_filter.get()
        date_pay = self.date_pay_entry.get()  # Use get_date() for tkcalendar DateEntry
        
        # Convert date_pay to string in 'YYYY-MM-DD' format
        date_pay_str = date_pay
        
        self.display_students(filter_name=search_text, filter_class=selected_class, filter_date_pay=date_pay_str)

    def edit_student(self, student_id):
        self.add_student_form.load_student_data(student_id)

    def delete_student(self, student_id):
        confirmation = messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cet étudiant ?")
        if confirmation:  # Si l'utilisateur confirme
            # Logique pour supprimer l'étudiant
            self.cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
            self.conn.commit()
            messagebox.showinfo("Succès", "Étudiant supprimé avec succès.")
        else:
            messagebox.showinfo("Annulé", "La suppression a été annulée.")
        self.display_students()  # Rafraîchir la table
    
    def print_student(self, sid):
        """Générer un reçu bilingue pour un étudiant avec un QR code et envoi WhatsApp."""

        # Récupérer les informations de l'étudiant
        self.cursor.execute("SELECT * FROM students WHERE id = ?", (sid,))
        student = self.cursor.fetchone()

        if not student:
            print("Étudiant introuvable.")
            return

        # Décomposez les données de l'étudiant (ajustez selon votre base de données)
        student_id, name, gender, class_name, subject, date_register, parent_number, price, date_pay, discount = student

        # Chemin pour sauvegarder le PDF dans le dossier Desktop
        month_name = datetime.now().strftime("%B-%Y")  # Nom du mois actuel
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", f"etudiant-{month_name}")
        os.makedirs(desktop_path, exist_ok=True)
        pdf_filename = f"recu_etudiant_{name.replace(' ', '_')}_{sid}.pdf"
        pdf_path = os.path.join(desktop_path, pdf_filename)

        # Document setup
        doc = SimpleDocTemplate(pdf_path, pagesize=A4,rightPadding=0, leftPadding=0, 
                                topPadding=0, bottomPadding=0,
                                leftMargin=0, rightMargin=0, 
                                topMargin=0, bottomMargin=0)
        styles = getSampleStyleSheet()
        elements = []

        # Register Arabic font
        arabic_font_path = "./res/Amiri-Regular.ttf"  # Ensure this file exists
        pdfmetrics.registerFont(TTFont('Amiri', arabic_font_path))

        # Arabic style
        arabic_style = ParagraphStyle(
            name='ArabicStyle',
            fontName='Amiri',
            fontSize=10,
            alignment=1
        )
        nbstyle = ParagraphStyle(
            name='ArabicStyle',
            fontName='Amiri',
            fontSize=8,
            alignment=1,
            textColor="#dddddd"
        )
       

        # Arabic Paragraphs stored in a dictionary for easy reference
        def reshape_arabic(text):
            return get_display(arabic_reshaper.reshape(text))

        arabic_texts = {
            "student_name": reshape_arabic("اســم الــطالب"),
            "gender": reshape_arabic("الجــنس"),
            "class": reshape_arabic("القــسم"),
            "subject": reshape_arabic("المــواد"),
            "parent_phone": reshape_arabic("رقــم الوكــيل"),
            "registration_date": reshape_arabic("تاريخ التسجيــل"),
            "payment_date": reshape_arabic("تـــاريخ الـدفع"),
            "amount_paid": reshape_arabic("المــبلغ المدفـوع"),
            "remaining_amount": reshape_arabic("المــبلغ المــتبقي"),
            "status": reshape_arabic("الحــالة"),
            "recu": reshape_arabic("إيصـال"),
            "payé": reshape_arabic("تم الــدفع"),
            "non_payé": reshape_arabic("لم يتم الــدفع"),
            "student_info": reshape_arabic("معــــلومــات الــطالــب"),
            "details_payment": reshape_arabic("تفــــاصيــل الــدفع"),
            "message": reshape_arabic("نـرجو منك الاحتفــاظ بهذا الإيصــال بــعناية. قــد تحتاجه في المستقـــبل لتـــأكيد أنـــك قد قـــمت بالدفع.")
        }
        current_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Ajouter un logo (si disponible)
        logo_path = "./img/header.jpg"  # Assurez-vous que ce fichier existe
        if os.path.exists(logo_path):
            logo = Image(logo_path)
            logo.drawHeight = 1 * inch
            logo.drawWidth = A4[0]  # Largeur complète de la page
            logo.hAlign = 'CENTER'
            elements.append(logo)

        # Ajouter un titre "Reçu"
        elements.append(Spacer(1, 20))
        title = Paragraph(f"Reçu : {arabic_texts['recu']}",arabic_style)
        elements.append(title)
        elements.append(Spacer(1, 30))

        # Table des informations de l'étudiant
        student_info = [
            ["Nom de l'étudiant", name, Paragraph(arabic_texts["student_name"], arabic_style)],
            ["Genre", gender, Paragraph(arabic_texts["gender"], arabic_style)],
            ["Classe", class_name, Paragraph(arabic_texts["class"], arabic_style)],
            ["Matière", subject, Paragraph(arabic_texts["subject"], arabic_style)],
            ["Téléphone du parent", parent_number, Paragraph(arabic_texts["parent_phone"], arabic_style)],
            ["Date d'inscription", date_register, Paragraph(arabic_texts["registration_date"], arabic_style)],
        ]
        student_table = Table(student_info, colWidths=[100, 300, 100], hAlign='CENTER')
        student_info_title = Paragraph(f"Informations sur les étudiants | {arabic_texts['student_info']}", arabic_style)        
        elements.append(student_info_title)
        elements.append(Spacer(1, 10))
        student_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Amiri'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightgrey, colors.white]),
            ('ROWHEIGHTS', (0, 0), (-1, -1), 10),  # Set height of all rows to 10px (0-based indexing)
        ]))
        elements.append(student_table)
        elements.append(Spacer(1, 30))

        # Table des détails de paiement
        details_data = [
            ["Date de paiement", date_pay if date_pay else current_datetime, Paragraph(arabic_texts["payment_date"], arabic_style)],
            ["Montant payé", f"{price} MRU", Paragraph(arabic_texts["amount_paid"], arabic_style)],
            ["Montant restant", f"{discount} MRU", Paragraph(arabic_texts["remaining_amount"], arabic_style)],
            ["Décision", Paragraph(f"Payé | {arabic_texts['payé']}",arabic_style) if (price > 0 and discount == 0) else Paragraph(f"Non Payé | {arabic_texts['non_payé']}",arabic_style), Paragraph(arabic_texts["status"], arabic_style)],
        ]
        details_info_title = Paragraph(f"Informations de paiement | {arabic_texts['details_payment']}", arabic_style)
        elements.append(details_info_title)
        elements.append(Spacer(1, 10))
        details_table = Table(details_data, colWidths=[100, 300, 100], hAlign='CENTER')
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Amiri'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightgrey, colors.white]),
        ]))
        elements.append(details_table)
        elements.append(Spacer(1, 50))

        # Générer un QR code
        qr_data = (
            f"Étudiant : {name}\n"
            f"Classe : {class_name}\n"
            f"Matière : {subject}\n"
            f"Montant payé : {price} MRU\n"
            f"Dette : {discount} MRU\n"
            f"Téléphone : {parent_number}\n"
            f"Généré le : {current_datetime}"
        )
        qr_code = qrcode.make(qr_data)
        qr_path = os.path.join(desktop_path, f"qr_etudiant_{sid}.png")
        qr_code.save(qr_path)

        # Ajouter le QR code
        qr_image = Image(qr_path)
        qr_image.drawHeight = 2 * inch
        qr_image.drawWidth = 2 * inch
        qr_image.hAlign = 'CENTER'
        elements.append(Spacer(1, 50))
        elements.append(qr_image)

        # Ajouter la date/heure sous le QR code
        qr_datetime = Paragraph(
            f"<font size=6 color='#000'><b>{current_datetime}</b></font>", styles['Title']
        )
        elements.append(Spacer(1, 10))
        elements.append(qr_datetime)
        nbar = Paragraph(f"{arabic_texts['message']}", nbstyle)
        elements.append(nbar)
        nbfr = Paragraph(f"Nous vous prions de bien vouloir conserver ce reçu. Il pourrait vous être utile à l'avenir pour confirmer que vous avez effectué le paiement",nbstyle)
        elements.append(nbfr)

        # Fetch school name for the header
        conn = sqlite3.connect('./db/school_account.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users LIMIT 1")
        school_name = cursor.fetchone()[0]
        conn.close()
        school = Paragraph(
            f"<font size=10 color='#CCCCCC'><b>{school_name}\n{month_name}</b></font>", styles['Normal']
        )
        elements.append(Spacer(1, 40))
        elements.append(school)

        # Générer le PDF
        doc.build(elements)
        print(f"Reçu généré : {pdf_path}")

        # Ouvrir automatiquement le PDF
        os.startfile(pdf_path)
        
        # Envoyer un message WhatsApp
        if 'pywhatkit' in globals():
            message = qr_data
            phone_numbers = [parent_number,"41378794","26677679","43000038"]
            for number in phone_numbers:
                try:
                    # Ajout automatique de l'indicatif pays si nécessaire
                    full_number = f"+{number}"
                    pywhatkit.sendwhatmsg_instantly(full_number, message)
                    print(f"Message envoyé avec succès à {full_number}.")
                except Exception as e:
                    print(f"Échec de l'envoi du message à {full_number} : {e}")

    
class AddStudentForm(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.student_id = None  # Suivi de l'état "édition"
        
        # Get the current date
        current_date = datetime.now().strftime('%Y-%m-%d')  # Current date in 'YYYY-MM-DD' format
        
        # Titre du formulaire
        self.label = ctk.CTkLabel(self, text="Enregistrer un nouvel étudiant", font=("Arial", 16))
        self.label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Champs de saisie
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Nom")
        self.name_entry.grid(row=1, column=0, padx=5, pady=5)
        
        self.gender_entry = ctk.CTkOptionMenu(self,fg_color="white",button_color="#4285F4",dropdown_fg_color="white",dropdown_hover_color="#4285F4",text_color="black", values=["Homme", "Femme"])
        self.gender_entry.set("")
        self.gender_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.class_entry = ctk.CTkOptionMenu(self,fg_color="white",button_color="#4285F4",dropdown_fg_color="white",dropdown_hover_color="#4285F4",text_color="black", values=["3As", "4As", "5C", "5D", "6C1","6C2", "6D", "7C", "7D1","7D2","P.E","S.C","English","Français"])
        self.class_entry.set("")
        self.class_entry.grid(row=2, column=0, padx=5, pady=5)
        
        self.subject_entry = ctk.CTkEntry(self, placeholder_text="Matière")
        self.subject_entry.grid(row=2, column=1, padx=5, pady=5)
        self.subject_entry.insert(0, "Tous")  # Set the initial value

        
        # Set the current date as the default value for 'Date d'inscription' and 'Date de paiement'
        self.date_register_entry = ctk.CTkEntry(self, placeholder_text="Date d'inscription")
        self.date_register_entry.grid(row=3, column=0, padx=5, pady=5)
        self.date_register_entry.insert(0, current_date)  # Set the initial value
        
        self.parent_number_entry = ctk.CTkEntry(self, placeholder_text="Numéro des parents")
        self.parent_number_entry.grid(row=3, column=1, padx=5, pady=5)
        
        self.price_entry = ctk.CTkEntry(self, placeholder_text="Prix")
        self.price_entry.grid(row=4, column=0, padx=5, pady=5)
        self.price_entry.insert(0, 0)  # Set the initial value

        self.date_pay_entry = ctk.CTkEntry(self, placeholder_text="Date de paiement")
        self.date_pay_entry.grid(row=4, column=1, padx=5, pady=5)
        
        self.discount_entry = ctk.CTkEntry(self, placeholder_text="Dette due")
        self.discount_entry.grid(row=5, column=0, padx=5, pady=5)
        self.discount_entry.insert(0, 0)  # Set the initial value

        
        # Bouton Enregistrer
        self.add_button = ctk.CTkButton(self,fg_color="#4285F4", text="Enregistrer", command=self.save_student)
        self.add_button.grid(row=6, column=0, columnspan=2, pady=10)
        # Create the top border as a thin frame
        self.return_frame_border = ctk.CTkFrame(self, fg_color="#ddd", height=5)
        self.return_frame_border.grid(row=7, column=0,columnspan=2, sticky="ew")  # Position above return_frame

        
        self.return_price_button = ctk.CTkButton(self,fg_color="#4285F4",text="Nouveau mois", command=self.update_price)
        self.return_price_button.grid(row=8, column=0, padx=5, pady=5 , sticky="w")
        self.delete_all_students_button = ctk.CTkButton(self,fg_color="#4285F4",text="Supprimer Tous")
        self.delete_all_students_button.grid(row=8, column=1, padx=5, pady=5 , sticky="e")
    def check_password(self, entered_password):
        # Connect to the database and fetch the password from the users table
        conn = sqlite3.connect('./db/school_account.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users LIMIT 1")  # Assuming id=1 is the user you're checking for
        db_password = cursor.fetchone()[0]
        conn.close()

        # Compare entered password with the stored password
        return entered_password == db_password

    def update_price(self):
        # Prompt the user for a password
        entered_password = simpledialog.askstring("Password", "Please enter the password:", show="*")

        if entered_password and self.check_password(entered_password):
            # Confirm action in French
            confirmation = messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir mettre à jour tous les prix à 0 ?")
            if confirmation:
                # Connect to the second database and update prices in the students table
                conn = sqlite3.connect('./db/student_school.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE students SET price = 0 , discount = 0,date_pay = NULL",)  # Update price to 0 for all students
                conn.commit()
                conn.close()

                # Notify the user that the operation was successful
                messagebox.showinfo("Succès", "Tous les prix ont été mis à jour à 0.")
        else:
            messagebox.showerror("Erreur", "Mot de passe incorrect.")

    def load_student_data(self, student_id):
        """Charger les données d'un étudiant existant dans le formulaire."""
        self.student_id = student_id
        self.parent.cursor.execute("SELECT * FROM students WHERE id = ?", (self.student_id,))
        student_data = self.parent.cursor.fetchone()
        
        # Remplir le formulaire avec les données existantes
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, student_data[1])
        
        self.gender_entry.set(student_data[2])
        self.class_entry.set(student_data[3])
        self.subject_entry.delete(0, "end")
        self.subject_entry.insert(0, student_data[4])
        self.date_register_entry.delete(0, "end")
        self.date_register_entry.insert(0, student_data[5])  # Use existing date_register
        self.parent_number_entry.delete(0, "end")
        self.parent_number_entry.insert(0, student_data[6])
        self.price_entry.delete(0, "end")
        self.price_entry.insert(0, str(student_data[7]))
        self.date_pay_entry.delete(0, "end")
        # self.date_pay_entry.insert(0, student_data[8])  # Use existing date_pay
        self.discount_entry.delete(0, "end")
        self.discount_entry.insert(0, str(student_data[9]))
        
        self.label.configure(text="Modifier les informations de l'étudiant")

    def save_student(self):
        """Enregistrer un étudiant (nouveau ou existant) dans la base de données."""
        student_data = (
            self.name_entry.get(),
            self.gender_entry.get(),
            self.class_entry.get(),
            self.subject_entry.get(),
            self.date_register_entry.get(),
            self.parent_number_entry.get(),
            float(self.price_entry.get()),
            self.date_pay_entry.get(),
            float(self.discount_entry.get()),
        )
        
        if self.student_id:
            # Mettre à jour l'étudiant existant
            self.parent.cursor.execute(
                '''UPDATE students SET name=?, gender=?, class=?, subject=?, date_register=?, parent_number=?, price=?, date_pay=?, discount=? WHERE id=?''',
                student_data + (self.student_id,)
            )
            self.student_id = None
            self.label.configure(text="Enregistrer un nouvel étudiant")
            messagebox.showinfo("Succès", "Étudiant modifié avec succès.")
        else:
            # Insérer un nouvel étudiant
            self.parent.cursor.execute(
                '''INSERT INTO students (name, gender, class, subject, date_register, parent_number, price, date_pay, discount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                student_data
            )
            messagebox.showinfo("Succès", "Étudiant ajouté avec succès.")

        self.parent.conn.commit()
        self.parent.display_students()  # Rafraîchir la liste des étudiants
        self.clear_form()


    def clear_form(self):
        """Effacer tous les champs du formulaire."""
        self.name_entry.delete(0, "end")
        self.gender_entry.set("")
        self.subject_entry.delete(0, "end")
        self.subject_entry.insert(0, "Tous")
        self.parent_number_entry.delete(0, "end")
        self.price_entry.delete(0,"end")
        self.price_entry.insert(0,"0.0")
        self.date_pay_entry.delete(0, "end")
        self.discount_entry.delete(0,"end")
        self.discount_entry.insert(0,"0.0")