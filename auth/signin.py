import customtkinter as ctk
import sqlite3

class RegisterWindow(ctk.CTkFrame):
    def __init__(self, root, go_to_login):
        super().__init__(root)

        self.go_to_login = go_to_login

        self.label = ctk.CTkLabel(self, text="S'inscrire", font=("Arial", 24))
        self.label.pack(pady=10)

        # Définir la largeur à 90 % de la largeur de la fenêtre (500px * 0.9 = 450px)
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Nom", width=450)
        self.name_entry.pack(pady=5)

        self.number_entry = ctk.CTkEntry(self, placeholder_text="Numéro scolaire", width=450)
        self.number_entry.pack(pady=5)

        self.type_entry = ctk.CTkOptionMenu(self,fg_color="white",button_color="#4285F4",dropdown_fg_color="white",dropdown_hover_color="#4285F4",text_color="black", values=["École", "Centre"], width=450)
        self.type_entry.pack(pady=5)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Mot de passe", show="•", width=450)
        self.password_entry.pack(pady=5)

        self.password_again_entry = ctk.CTkEntry(self, placeholder_text="Répéter le mot de passe", show="•", width=450)
        self.password_again_entry.pack(pady=5)

        # Cadre des boutons
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.pack(padx=90, pady=10, fill="x")
        # Bouton retour à la connexion
        self.back_to_login_button = ctk.CTkButton(self.buttons_frame,text_color="gray", text="Retour à la connexion", fg_color="transparent", border_width=1, border_color="#565b5e", command=self.go_to_login)
        self.back_to_login_button.pack(side="left", padx=10)
        # Bouton Créer un compte
        self.register_button = ctk.CTkButton(self.buttons_frame,fg_color="#4285F4", text="Créer un compte", command=self.register)
        self.register_button.pack(side="right", padx=10)

    def register(self):
        name = self.name_entry.get()
        number = self.number_entry.get()
        type_ = self.type_entry.get()
        password = self.password_entry.get()
        password_again = self.password_again_entry.get()

        if password != password_again:
            print("Les mots de passe ne correspondent pas")
            return

        conn = sqlite3.connect("./db/school_account.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                         (name TEXT, number TEXT UNIQUE, type TEXT, password TEXT)''')
        try:
            cursor.execute("INSERT INTO users (name, number, type, password) VALUES (?, ?, ?, ?)",
                           (name, number, type_, password))
            conn.commit()
            print("Compte créé avec succès")
            self.go_to_login()  # Rediriger vers la page de connexion après la création du compte
        except sqlite3.IntegrityError:
            print("L'utilisateur existe déjà")
        finally:
            conn.close()
