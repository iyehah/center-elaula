import customtkinter as ctk
import sqlite3

class StudentTab(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)
        
        # Connexion à la base de données et création de la table des étudiants si elle n'existe pas
        self.conn = sqlite3.connect("student_school.db")
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
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.grid(row=0, column=0, padx=10, pady=10, columnspan=2, sticky="nsew")
        
        # Champ de recherche
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Rechercher par nom")
        self.search_entry.grid(row=0, column=0, padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", self.filter_students)
        
        # Filtre par classe
        self.class_filter = ctk.CTkComboBox(self.search_frame, values=["Tous", "3As", "4As", "5C", "5D", "6C", "6D", "7C", "7D"])
        self.class_filter.set("Tous")
        self.class_filter.grid(row=0, column=1, padx=5, pady=5)
        self.class_filter.bind("<<ComboboxSelected>>", self.filter_students)
        
        # Cadre de la table des étudiants
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Configurer les colonnes pour occuper 80% de la fenêtre
        self.grid_columnconfigure(0, weight=1)  # Cela permettra à la table d'occuper 80% de la largeur de la fenêtre
        
        # Créer un cadre défilant pour le contenu de la table
        self.scrollable_frame = ctk.CTkScrollableFrame(self.table_frame, width=970, height=360)
        self.scrollable_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # En-têtes de table
        self.headers = ["Nom", "Genre", "Classe", "Matière", "Date d'inscription", "Numéro des parents", "Prix", "Date de paiement", "Remise", "Actions"]
        
        # Configurer les colonnes pour prendre un espace égal
        num_columns = len(self.headers)
        for col in range(num_columns):
            self.scrollable_frame.grid_columnconfigure(col, weight=1)
        
        # Ajouter les labels d'en-tête
        for col, header in enumerate(self.headers):
            header_label = ctk.CTkLabel(self.scrollable_frame, text=header, font=("Arial", 12, "bold"), padx=5, pady=5, fg_color="#1f6aa5")
            header_label.grid(row=0, column=col, sticky="nsew")

        # Label en bas pour afficher le nombre d'étudiants
        self.count_label = ctk.CTkLabel(self.table_frame, text="Total des étudiants : 0", font=("Arial", 12))
        self.count_label.grid(row=1, column=0, padx=10, pady=10, sticky="s")

        # Cadre du formulaire d'ajout/édition d'étudiant
        self.add_student_form = AddStudentForm(self)
        self.add_student_form.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        # Afficher tous les étudiants au départ
        self.display_students()

    def display_students(self, filter_name="", filter_class="Tous"):
        """Récupérer et afficher les enregistrements des étudiants de la base de données selon les filtres."""
        # Effacer les lignes existantes
        for widget in self.scrollable_frame.winfo_children():
            if int(widget.grid_info()["row"]) > 0:  # Ne supprimer que les lignes de données (pas les en-têtes)
                widget.destroy()

        # Récupérer les données des étudiants selon les filtres
        query = "SELECT id, name, gender, class, subject, date_register, parent_number, price, date_pay, discount FROM students WHERE 1=1"
        params = []
        
        if filter_name:
            query += " AND name LIKE ?"
            params.append(f"%{filter_name}%")
        
        if filter_class != "Tous":
            query += " AND class = ?"
            params.append(filter_class)
        
        self.cursor.execute(query, params)
        students = self.cursor.fetchall()

        # Remplir la table avec les données des étudiants
        for row, student in enumerate(students, start=1):  # Commencer à la ligne 1 pour laisser de l'espace pour les en-têtes
            student_id, *student_data = student
            for col, data in enumerate(student_data):
                cell = ctk.CTkLabel(self.scrollable_frame, text=data, padx=5, pady=5)
                cell.grid(row=row, column=col, sticky="nsew")
            
            # Cadre contenant les actions (boutons Editer/Supprimer) dans une seule colonne
            actions_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            actions_frame.grid(row=row, column=len(self.headers)-1, padx=5, pady=5, sticky="nsew")

            # Bouton Editer
            edit_button = ctk.CTkButton(actions_frame, text="Editer", width=50, command=lambda sid=student_id: self.edit_student(sid))
            edit_button.pack(side="left", expand=True, padx=5, pady=5)

            # Bouton Supprimer
            delete_button = ctk.CTkButton(actions_frame, text="Supprimer", width=60, command=lambda sid=student_id: self.delete_student(sid))
            delete_button.pack(side="left", expand=True, padx=5, pady=5)

        # Mettre à jour le label du nombre total d'étudiants
        self.count_label.configure(text=f"Total des étudiants : {len(students)}")

    def filter_students(self, event=None):
        """Filtrer les étudiants selon le champ de recherche et le filtre par classe."""
        search_text = self.search_entry.get().strip()
        selected_class = self.class_filter.get()
        self.display_students(filter_name=search_text, filter_class=selected_class)

    def edit_student(self, student_id):
        self.add_student_form.load_student_data(student_id)

    def delete_student(self, student_id):
        self.cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        self.conn.commit()
        self.display_students()  # Rafraîchir la table

class AddStudentForm(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.student_id = None  # Suivi de l'état "édition"
        
        # Titre du formulaire
        self.label = ctk.CTkLabel(self, text="Enregistrer un nouvel étudiant", font=("Arial", 16))
        self.label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Champs de saisie
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Nom")
        self.name_entry.grid(row=1, column=0, padx=5, pady=5)
        
        self.gender_entry = ctk.CTkComboBox(self, values=["Homme", "Femme"])
        self.gender_entry.set("Sélectionner le genre")
        self.gender_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.class_entry = ctk.CTkComboBox(self, values=["3As", "4As", "5C", "5D", "6C", "6D", "7C", "7D"])
        self.class_entry.set("Sélectionner la classe")
        self.class_entry.grid(row=2, column=0, padx=5, pady=5)
        
        self.subject_entry = ctk.CTkEntry(self, placeholder_text="Matière")
        self.subject_entry.grid(row=2, column=1, padx=5, pady=5)
        
        self.date_register_entry = ctk.CTkEntry(self, placeholder_text="Date d'inscription")
        self.date_register_entry.grid(row=3, column=0, padx=5, pady=5)
        
        self.parent_number_entry = ctk.CTkEntry(self, placeholder_text="Numéro des parents")
        self.parent_number_entry.grid(row=3, column=1, padx=5, pady=5)
        
        self.price_entry = ctk.CTkEntry(self, placeholder_text="Prix")
        self.price_entry.grid(row=4, column=0, padx=5, pady=5)
        
        self.date_pay_entry = ctk.CTkEntry(self, placeholder_text="Date de paiement")
        self.date_pay_entry.grid(row=4, column=1, padx=5, pady=5)
        
        self.discount_entry = ctk.CTkEntry(self, placeholder_text="Remise")
        self.discount_entry.grid(row=5, column=0, padx=5, pady=5)
        
        # Bouton Enregistrer
        self.add_button = ctk.CTkButton(self, text="Enregistrer", command=self.save_student)
        self.add_button.grid(row=6, column=0, columnspan=2, pady=10)

    def load_student_data(self, student_id):
        """Charger les données de l'étudiant dans le formulaire pour l'édition."""
        self.student_id = student_id
        self.parent.cursor.execute("SELECT * FROM students WHERE id = ?", (self.student_id,))
        student_data = self.parent.cursor.fetchone()
        
        # Remplir les champs du formulaire avec les données existantes
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, student_data[1])
        
        self.gender_entry.set(student_data[2])
        self.class_entry.set(student_data[3])
        self.subject_entry.delete(0, "end")
        self.subject_entry.insert(0, student_data[4])
        self.date_register_entry.delete(0, "end")
        self.date_register_entry.insert(0, student_data[5])
        self.parent_number_entry.delete(0, "end")
        self.parent_number_entry.insert(0, student_data[6])
        self.price_entry.delete(0, "end")
        self.price_entry.insert(0, str(student_data[7]))
        self.date_pay_entry.delete(0, "end")
        self.date_pay_entry.insert(0, student_data[8])
        self.discount_entry.delete(0, "end")
        self.discount_entry.insert(0, str(student_data[9]))
        
        self.label.configure(text="Modifier les informations de l'étudiant")

    def save_student(self):
        """Enregistrer un nouvel étudiant ou modifier un étudiant existant dans la base de données."""
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
            # Mettre à jour l'enregistrement existant de l'étudiant
            self.parent.cursor.execute(
                '''UPDATE students SET name=?, gender=?, class=?, subject=?, date_register=?, parent_number=?, price=?, date_pay=?, discount=? WHERE id=?''',
                student_data + (self.student_id,)
            )
            self.student_id = None
            self.label.configure(text="Enregistrer un nouvel étudiant")
        else:
            # Insérer un nouvel enregistrement d'étudiant
            self.parent.cursor.execute(
                '''INSERT INTO students (name, gender, class, subject, date_register, parent_number, price, date_pay, discount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                student_data
            )
        
        self.parent.conn.commit()
        self.parent.display_students()  # Rafraîchir la table des étudiants
        self.clear_form()

    def clear_form(self):
        """Effacer les champs du formulaire."""
        self.name_entry.delete(0, "end")
        self.gender_entry.set("Sélectionner le genre")
        self.class_entry.set("Sélectionner la classe")
        self.subject_entry.delete(0, "end")
        self.date_register_entry.delete(0, "end")
        self.parent_number_entry.delete(0, "end")
        self.price_entry.delete(0, "end")
        self.date_pay_entry.delete(0, "end")
        self.discount_entry.delete(0, "end")
