import customtkinter as ctk
import sqlite3
from tkinter import messagebox


class TeacherTab(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)
        
        # Connexion à la base de données et création de la table des enseignants si elle n'existe pas
        self.conn = sqlite3.connect("teacher_school.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS teachers (
                                id INTEGER PRIMARY KEY,
                                name TEXT,
                                class TEXT,
                                subject TEXT,
                                salary REAL,
                                number TEXT,
                                percentage REAL
                            )''')
        self.conn.commit()

        # Cadre de recherche et de filtre
        self.search_frame = ctk.CTkFrame(self,fg_color="#DBDBDB")
        self.search_frame.grid(row=0, column=0, padx=10, pady=10, columnspan=2, sticky="nsew")
        
        # Champ de recherche
        self.search_entry = ctk.CTkEntry(self.search_frame, width=300, placeholder_text="Rechercher par nom")
        self.search_entry.grid(row=0, column=0, padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", self.filter_teachers)
        
        # Filtre par classe
        self.class_filter = ctk.CTkOptionMenu(self.search_frame,fg_color="white",button_color="#4285F4",dropdown_fg_color="white",dropdown_hover_color="#4285F4",text_color="black",width=200, values=["Tous", "3As", "4As", "5C", "5D", "6C1","6C2", "6D", "7C", "7D1","7D2","P.E","S.C","English","Français"])
        self.class_filter.set("Tous")
        self.class_filter.grid(row=0, column=1, padx=5, pady=5)
        self.class_filter.bind("<<ComboboxSelected>>", self.filter_teachers)
        
        # "Filtre par classe" button
        self.filter_button = ctk.CTkButton(self.search_frame,fg_color="#4285F4", text="Filtrer par classe", command=self.filter_teachers)
        self.filter_button.grid(row=0, column=2, padx=5, pady=5)

        # Cadre pour le tableau des enseignants
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Configurer les colonnes pour occuper 80 % de la largeur de la fenêtre
        self.grid_columnconfigure(0, weight=1)  # Cela permet au tableau de prendre 80 % de la largeur de la fenêtre
        
        # Créer un cadre défilable pour le contenu du tableau
        self.scrollable_frame = ctk.CTkScrollableFrame(self.table_frame, width=970, height=500,fg_color="#CFCFCF")
        self.scrollable_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # En-têtes du tableau
        self.headers = ["Nom", "Classe", "Matière", "Salaire", "Numéro", "Pourcentage", "Actions"]
        
        # Configurer les colonnes pour occuper un espace égal
        num_columns = len(self.headers)
        for col in range(num_columns):
            self.scrollable_frame.grid_columnconfigure(col, weight=1)
        
        # Ajouter les étiquettes d'en-tête
        for col, header in enumerate(self.headers):
            header_label = ctk.CTkLabel(self.scrollable_frame, text=header, font=("Arial", 12, "bold"), padx=5, pady=5,text_color="white", fg_color="#4285F4")
            header_label.grid(row=0, column=col, sticky="nsew")

        # Étiquette en bas pour afficher le nombre d'enseignants
        self.count_label = ctk.CTkLabel(self.table_frame, text="Total des enseignants : 0", font=("Arial", 12))
        self.count_label.grid(row=1, column=0, padx=10, pady=10, sticky="s")

        # Formulaire d'ajout/modification des enseignants
        self.add_teacher_form = AddTeacherForm(self)
        self.add_teacher_form.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        # Afficher tous les enseignants au départ
        self.display_teachers()

    def display_teachers(self, filter_name="", filter_class="Tous"):
        """Récupérer et afficher les enregistrements des enseignants selon les filtres."""
        # Effacer les lignes existantes
        for widget in self.scrollable_frame.winfo_children():
            if int(widget.grid_info()["row"]) > 0:  # Ne supprimer que les lignes de données (pas les en-têtes)
                widget.destroy()

        # Récupérer les données des enseignants selon les filtres
        query = "SELECT id, name, class, subject, salary, number, percentage FROM teachers WHERE 1=1"
        params = []
        
        if filter_name:
            query += " AND name LIKE ?"
            params.append(f"%{filter_name}%")
        
        if filter_class != "Tous":
            query += " AND class = ?"
            params.append(filter_class)
        
        self.cursor.execute(query, params)
        teachers = self.cursor.fetchall()

        # Remplir le tableau avec les données des enseignants
        for row, teacher in enumerate(teachers, start=1):  # Commencer à la ligne 1 pour laisser de l'espace pour les en-têtes
            teacher_id, *teacher_data = teacher
            for col, data in enumerate(teacher_data):
                cell = ctk.CTkLabel(self.scrollable_frame, text=data, padx=5, pady=5)
                cell.grid(row=row, column=col, sticky="nsew")
            
            # Cadre pour les actions (boutons Modifier/Supprimer) dans une seule colonne
            actions_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            actions_frame.grid(row=row, column=len(self.headers)-1, padx=5, pady=5, sticky="nsew")

            # Bouton Modifier
            edit_button = ctk.CTkButton(actions_frame, text="Modifier", width=50, command=lambda tid=teacher_id: self.edit_teacher(tid))
            edit_button.pack(side="left", expand=True, padx=5, pady=5)

            # Bouton Supprimer
            delete_button = ctk.CTkButton(actions_frame, text="Supprimer", width=60, command=lambda tid=teacher_id: self.delete_teacher(tid))
            delete_button.pack(side="left", expand=True, padx=5, pady=5)

        # Mettre à jour l'étiquette du nombre total d'enseignants
        self.count_label.configure(text=f"Total des enseignants : {len(teachers)}")

    def filter_teachers(self, event=None):
        """Filtrer les enseignants en fonction de la recherche et du filtre de classe."""
        search_text = self.search_entry.get().strip()
        selected_class = self.class_filter.get()
        self.display_teachers(filter_name=search_text, filter_class=selected_class)

    def edit_teacher(self, teacher_id):
        self.add_teacher_form.load_teacher_data(teacher_id)

    def delete_teacher(self, teacher_id):
        confirmation = messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cet enseignant ?")
        if confirmation:  # Si l'utilisateur confirme
            # Logique pour supprimer l'enseignant
            self.cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
            self.conn.commit()
            messagebox.showinfo("Succès", "Enseignant supprimé avec succès.")
        else:
            messagebox.showinfo("Annulé", "La suppression a été annulée.")
        self.display_teachers()  # Actualiser le tableau

class AddTeacherForm(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.teacher_id = None  # Suivre si nous sommes en mode "modification"
        
        # Titre du formulaire
        self.label = ctk.CTkLabel(self, text="Enregistrer un nouvel enseignant", font=("Arial", 16))
        self.label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Champs de saisie
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Nom")
        self.name_entry.grid(row=1, column=0, padx=5, pady=5)
        
        self.class_entry = ctk.CTkOptionMenu(self,fg_color="white",button_color="#4285F4",dropdown_fg_color="white",dropdown_hover_color="#4285F4",text_color="black",values=["3As", "4As", "5C", "5D", "6C1","6C2", "6D", "7C", "7D1","7D2","P.E","S.C","English","Français"])
        self.class_entry.set("")
        self.class_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.subject_entry = ctk.CTkEntry(self, placeholder_text="Matière")
        self.subject_entry.grid(row=2, column=0, padx=5, pady=5)
        
        self.salary_entry = ctk.CTkEntry(self, placeholder_text="Salaire")
        self.salary_entry.grid(row=2, column=1, padx=5, pady=5)
        
        self.number_entry = ctk.CTkEntry(self, placeholder_text="Numéro de contact")
        self.number_entry.grid(row=3, column=0, padx=5, pady=5)
        
        self.percentage_entry = ctk.CTkEntry(self, placeholder_text="Pourcentage")
        self.percentage_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Bouton Enregistrer
        self.add_button = ctk.CTkButton(self,fg_color="#4285F4", text="Enregistrer", command=self.save_teacher)
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10)

    def load_teacher_data(self, teacher_id):
        """Charger les données de l'enseignant dans le formulaire pour modification."""
        self.teacher_id = teacher_id
        self.parent.cursor.execute("SELECT * FROM teachers WHERE id = ?", (self.teacher_id,))
        teacher_data = self.parent.cursor.fetchone()
        
        # Remplir les champs du formulaire avec les données existantes
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, teacher_data[1])
        
        self.class_entry.set(teacher_data[2])
        self.subject_entry.delete(0, "end")
        self.subject_entry.insert(0, teacher_data[3])
        self.salary_entry.delete(0, "end")
        self.salary_entry.insert(0, str(teacher_data[4]))
        self.number_entry.delete(0, "end")
        self.number_entry.insert(0, teacher_data[5])
        self.percentage_entry.delete(0, "end")
        self.percentage_entry.insert(0, str(teacher_data[6]))
        
        self.label.configure(text="Modifier les informations de l'enseignant")

    def save_teacher(self):
        """Enregistrer un nouvel enseignant ou mettre à jour un enseignant existant dans la base de données."""
        teacher_data = (
            self.name_entry.get(),
            self.class_entry.get(),
            self.subject_entry.get(),
            float(self.salary_entry.get()),
            self.number_entry.get(),
            float(self.percentage_entry.get()),
        )
        
        if self.teacher_id:
            # Mettre à jour l'enregistrement de l'enseignant existant
            self.parent.cursor.execute(
                '''UPDATE teachers SET name=?, class=?, subject=?, salary=?, number=?, percentage=? WHERE id=?''',
                teacher_data + (self.teacher_id,)
            )
            self.teacher_id = None
            self.label.configure(text="Enregistrer un nouvel enseignant")
            messagebox.showinfo("Succès", "Enseignant modifié avec succès.")
        else:
            # Insérer un nouvel enregistrement d'enseignant
            self.parent.cursor.execute(
                '''INSERT INTO teachers (name, class, subject, salary, number, percentage) VALUES (?, ?, ?, ?, ?, ?)''',
                teacher_data
            )
            messagebox.showinfo("Succès", "Enseignant ajouté avec succès.")

        
        self.parent.conn.commit()
        self.parent.display_teachers()  # Actualiser le tableau des enseignants
        self.clear_form()

    def clear_form(self):
        """Effacer les champs du formulaire."""
        self.name_entry.delete(0, "end")
        self.class_entry.set("")
        self.subject_entry.delete(0, "end")
        self.salary_entry.delete(0, "end")
        self.number_entry.delete(0, "end")
        self.percentage_entry.delete(0, "end")
