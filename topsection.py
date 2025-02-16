import customtkinter as ctk
import sqlite3

class TopSection(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)

        # Connexion aux bases de données
        self.conn_students = sqlite3.connect("student_school.db")
        self.cursor_students = self.conn_students.cursor()

        self.conn_teachers = sqlite3.connect("teacher_school.db")
        self.cursor_teachers = self.conn_teachers.cursor()

        self.conn_costs = sqlite3.connect("costs_school.db")
        self.cursor_costs = self.conn_costs.cursor()

        # Calcul des totaux
        total_revenue = self.get_total_revenue()
        total_dette = self.get_total_debt()
        total_salary = self.get_total_salary()
        total_costs = self.get_total_costs()

        # Calcul de la charge totale et de la différence
        total_charge = total_salary + total_costs
        total_difference = (total_revenue + total_dette) - total_charge

        # Données pour les cartes
        cards_data = [
            {"title": "Revenu Total", "value": f"{total_revenue:.2f} MRU", "subtitle": "Revenus totaux", "color": "#34A853"},
            {"title": "Dette totale", "value": f"{total_dette:.2f} MRU", "subtitle": "Dette totale restante", "color": "#00838F"},
            {"title": "Total Salaires", "value": f"{total_salary:.2f} MRU", "subtitle": "Salaires totaux", "color": "#FBBC05"},
            {"title": "Total des Coûts", "value": f"{total_costs:.2f} MRU", "subtitle": "Coûts totaux", "color": "#FF9900"},
            {"title": "Charges Totales", "value": f"{total_charge:.2f} MRU", "subtitle": "Charges totales", "color": "#EA4335"},
            {"title": "Revenu Restant", "value": f"{total_difference:.2f} MRU", "subtitle": "Revenu net", "color": "#4285F4"},
        ]

        # Configuration des colonnes pour l'espacement
        for col in range(len(cards_data)):
            self.grid_columnconfigure(col, weight=1, uniform="equal")  # Equal weight to all columns

        # Création de la section des cartes
        self.create_top_section(cards_data)

    def create_top_section(self, cards_data):
        """Créer une section supérieure avec des cartes."""
        # Create the container frame
        top_frame = ctk.CTkFrame(self, fg_color="#CFCFCF")
        top_frame.grid(row=0, column=0, columnspan=len(cards_data), padx=20, pady=20, sticky="nsew")
        
        # Configure responsive columns
        for col in range(len(cards_data)):
            top_frame.grid_columnconfigure(col, weight=1, uniform="equal")  # Ensure equal distribution

        # Create and add cards
        for index, card_data in enumerate(cards_data):
            self.create_card(card_data, top_frame, 0, index)  # All cards in row 0, each in a separate column

    def create_card(self, card_data, parent, row, column):
        """Créer une carte individuelle."""
        card = ctk.CTkFrame(parent, corner_radius=10, fg_color=card_data["color"], height=150)
        card.grid(row=row, column=column, padx=10, pady=20, sticky="ew")  # sticky="ew" for horizontal stretch

        title_label = ctk.CTkLabel(card, text=card_data["title"], font=ctk.CTkFont(size=14, weight="bold"),
                                   text_color="white")
        title_label.pack(pady=(10, 0))

        value_label = ctk.CTkLabel(card, text=card_data["value"], font=ctk.CTkFont(size=24, weight="bold"),
                                   text_color="white")
        value_label.pack(pady=(5, 0))

        subtitle_label = ctk.CTkLabel(card, text=card_data["subtitle"], font=ctk.CTkFont(size=12), text_color="white")
        subtitle_label.pack(pady=(0, 10))

    def get_total_revenue(self):
        """Obtenir le revenu total des étudiants."""
        try:
            self.cursor_students.execute("SELECT SUM(price) FROM students")
            result = self.cursor_students.fetchone()
            return result[0] if result[0] is not None else 0.0
        except sqlite3.OperationalError as e:
            print(f"Erreur SQL : {e}")
            return 0.0
    def get_total_debt(self):
            """Obtenir le dette total des étudiants."""
            try:
                self.cursor_students.execute("SELECT SUM(discount) FROM students")
                result = self.cursor_students.fetchone()
                return result[0] if result[0] is not None else 0.0
            except sqlite3.OperationalError as e:
                print(f"Erreur SQL : {e}")
                return 0.0

    def get_total_salary(self):
        """Obtenir le total des salaires des enseignants."""
        try:
            self.cursor_teachers.execute("SELECT SUM(salary) FROM teachers")
            result = self.cursor_teachers.fetchone()
            return result[0] if result and result[0] is not None else 0.0
        except sqlite3.OperationalError as e:
            print(f"Erreur SQL : {e}")
            return 0.0


    def get_total_costs(self):
        """Obtenir le total des coûts."""
        try:
            self.cursor_costs.execute("SELECT SUM(costs) FROM costs")
            result = self.cursor_costs.fetchone()
            # Vérification supplémentaire pour éviter les erreurs
            return result[0] if result and result[0] is not None else 0.0
        except sqlite3.OperationalError as e:
            print(f"Erreur SQL : {e}")
            return 0.0

