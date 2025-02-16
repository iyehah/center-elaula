import customtkinter as ctk
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.patches import Circle, Wedge, Patch


class StatisticsTab(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)
        
        # Configurer la disposition de la grille pour une meilleure organisation
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Se connecter aux bases de données des étudiants et des enseignants
        self.conn_etudiant = sqlite3.connect("student_school.db")
        self.conn_enseignant = sqlite3.connect("teacher_school.db")

        # Créer tous les graphiques
        self.creer_graphes()

    def creer_graphes(self):
        """Créer tous les graphiques dans l'onglet statistiques."""
        self.creer_graphique_prix_total_vs_salaire()
        self.creer_graphique_paiement_etudiant()
        self.creer_graphique_inscriptions_etudiants()
        self.creer_graphique_pourcentages_classes()

    def actualiser_graphes(self):
        """Actualiser tous les graphiques pour refléter les données mises à jour dans la base de données."""
        # Supprimer les graphiques/widgets existants de la grille
        for widget in self.winfo_children():
            widget.destroy()
        
        # Re-créer tous les graphiques
        self.creer_graphique_prix_total_vs_salaire()
        self.creer_graphique_paiement_etudiant()
        self.creer_graphique_inscriptions_etudiants()
        self.creer_graphique_pourcentages_classes()

    def creer_graphique_prix_total_vs_salaire(self):
        """Graphique en camembert : Prix total vs Salaire total avec légende"""
        curseur_etudiant = self.conn_etudiant.cursor()
        curseur_etudiant.execute("SELECT SUM(price) FROM students")
        prix_total = curseur_etudiant.fetchone()[0] or 0

        curseur_enseignant = self.conn_enseignant.cursor()
        curseur_enseignant.execute("SELECT SUM(salary) FROM teachers")
        salaire_total = curseur_enseignant.fetchone()[0] or 0

        # Données pour le graphique en camembert
        labels = ["Prix Total", "Salaire Total"]
        sizes = [prix_total, salaire_total]
        couleurs = ['#4CAF50', '#FF5722']

        # Tracer le graphique en camembert
        fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
        fig.patch.set_facecolor('#2E2E2E')
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                          startangle=140, colors=couleurs, textprops={'color': 'gainsboro'})
        ax.set_title("Prix Total vs Salaire Total", fontsize=12, color='gainsboro')
        ax.legend(loc="upper right", fontsize=8, facecolor='#504d4d', bbox_to_anchor=(1.5, 1), labelcolor='gainsboro', frameon=True, edgecolor='#333')
        ax.set_facecolor((0, 0, 0, 0))

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def creer_graphique_paiement_etudiant(self):
        """Graphique linéaire : Paiement des étudiants au fil du temps, sans bordure, seulement les axes X et Y."""
        curseur_etudiant = self.conn_etudiant.cursor()
        curseur_etudiant.execute("SELECT date_pay, price FROM students WHERE date_pay IS NOT NULL")
        data = curseur_etudiant.fetchall()

        dates, prix = [], []
        for date_pay, price in data:
            try:
                date_obj = datetime.strptime(date_pay, '%Y-%m-%d')
                dates.append(date_obj)
                prix.append(price)
            except ValueError:
                continue

        if dates and prix:
            sorted_data = sorted(zip(dates, prix), key=lambda x: x[0])
            sorted_dates, sorted_prix = zip(*sorted_data)

            fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
            fig.patch.set_facecolor('#2E2E2E')
            ax.plot(sorted_dates, sorted_prix, marker='o', linestyle='-', color='#1E90FF')
            ax.set_title("Paiement des Étudiants au Fil du Temps", fontsize=12, color='gainsboro')
            ax.set_xlabel("Date", fontsize=10, color='gainsboro')
            ax.set_ylabel("Prix", fontsize=10, color='gainsboro')
            ax.grid(True, color='#1E90FF', linewidth=0.1)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            # Définir la couleur de la bordure inférieure et gauche
            ax.spines['bottom'].set_color('#1E90FF')
            ax.spines['bottom'].set_linewidth(1)
            ax.spines['left'].set_color('#1E90FF')
            ax.spines['left'].set_linewidth(1)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            fig.autofmt_xdate()
            ax.tick_params(axis='x', colors='gainsboro')  # Couleur des étiquettes de l'axe X
            ax.tick_params(axis='y', colors='gainsboro')  # Couleur des étiquettes de l'axe Y
            ax.set_facecolor((0, 0, 0, 0))

            canvas = FigureCanvasTkAgg(fig, master=self)
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        else:
            no_data_label = ctk.CTkLabel(self, text="Aucune donnée de paiement étudiant disponible", font=("Arial", 12))
            no_data_label.grid(row=0, column=1, padx=10, pady=10)

    def creer_graphique_inscriptions_etudiants(self):
        """Graphique en barres : Inscriptions des étudiants par mois, sans bordure, seulement les axes X et Y."""
        curseur_etudiant = self.conn_etudiant.cursor()
        curseur_etudiant.execute("""
            SELECT strftime('%Y-%m', date_register) AS month, COUNT(*) 
            FROM students 
            GROUP BY month 
            ORDER BY month
        """)
        data = curseur_etudiant.fetchall()

        mois, comptes = [], []
        for month, count in data:
            try:
                month_obj = datetime.strptime(month, '%Y-%m')
                mois.append(month_obj)
                comptes.append(count)
            except ValueError:
                continue

        if mois and comptes:
            fig, ax = plt.subplots(figsize=(4, 2), dpi=100)
            fig.patch.set_facecolor('#2E2E2E')
            ax.bar(mois, comptes, color='#FFD700')
            ax.set_title("Inscriptions des Étudiants par Mois", fontsize=12, color='gainsboro')
            ax.set_xlabel("Mois", fontsize=10, color='gainsboro')
            ax.set_ylabel("Inscriptions", fontsize=10, color='gainsboro')
            ax.grid(True, color='#FFD700', linewidth=0.1)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            # Définir la couleur de la bordure inférieure et gauche
            ax.spines['bottom'].set_color('#FFD700')
            ax.spines['bottom'].set_linewidth(1)
            ax.spines['left'].set_color('#FFD700')
            ax.spines['left'].set_linewidth(1)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m'))
            fig.autofmt_xdate()
            ax.tick_params(axis='x', colors='gainsboro')  # Couleur des étiquettes de l'axe X
            ax.tick_params(axis='y', colors='gainsboro')  # Couleur des étiquettes de l'axe Y
            ax.set_facecolor((0, 0, 0, 0))

            canvas = FigureCanvasTkAgg(fig, master=self)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        else:
            no_data_label = ctk.CTkLabel(self, text="Aucune donnée d'inscription disponible", font=("Arial", 12))
            no_data_label.grid(row=1, column=0, padx=10, pady=10)

    def creer_graphique_pourcentages_classes(self):
        curseur_etudiant = self.conn_etudiant.cursor()
        # Récupérer le nombre d'étudiants par classe au fil du temps
        curseur_etudiant.execute("""
            SELECT class, date_register, COUNT(*) 
            FROM students 
            GROUP BY class, date_register 
            ORDER BY date_register
        """)
        data = curseur_etudiant.fetchall()

        if data:
            # Préparer les données
            classes = set(row[0] for row in data)
            données_classes = {cls: [] for cls in classes}
            dates = sorted(set(row[1] for row in data))

            # Organiser les données par classe et par date
            for cls in classes:
                données_classes[cls] = [0] * len(dates)  # initialiser les comptes avec des zéros
                for i, date in enumerate(dates):
                    # Trouver le nombre d'étudiants pour cette classe à cette date
                    count = next((row[2] for row in data if row[0] == cls and row[1] == date), 0)
                    données_classes[cls][i] = count
            
            # Tracer les données
            fig, ax = plt.subplots(figsize=(8, 3), dpi=100)
            fig.patch.set_facecolor('#2E2E2E')

            # Tracer chaque classe
            for idx, (cls, counts) in enumerate(données_classes.items()):
                ax.plot(dates, counts, label=cls, marker='o', color=plt.cm.tab20(idx / len(données_classes)))

            # Formatage de l'axe x (dates)
            ax.grid(True, color='#FFD700', linewidth=0.1)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            # Définir la couleur de la bordure inférieure et gauche
            ax.spines['bottom'].set_color('#FFD700')
            ax.spines['bottom'].set_linewidth(1)
            ax.spines['left'].set_color('#FFD700')
            ax.spines['left'].set_linewidth(1)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m'))
            fig.autofmt_xdate()
            ax.tick_params(axis='x', colors='gainsboro')  # Couleur des étiquettes de l'axe X
            ax.tick_params(axis='y', colors='gainsboro')  # Couleur des étiquettes de l'axe Y
            ax.set_xlabel('Date', fontsize=10, color='gainsboro')
            ax.set_ylabel('Nombre d\'Étudiants', fontsize=10, color='gainsboro')
            ax.set_title('Étudiants par Classe au Fil du Temps', fontsize=12, color='gainsboro')
            ax.legend(loc='upper right', fontsize=10, facecolor='#504d4d', bbox_to_anchor=(1.11, 1.1), labelcolor='gainsboro', frameon=True, edgecolor='#333')

            ax.set_facecolor((0, 0, 0, 0))
            # Rotation des étiquettes de dates pour une meilleure lisibilité
            plt.xticks(rotation=45, ha="right")

            # Intégrer le graphique dans tkinter
            canvas = FigureCanvasTkAgg(fig, master=self)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        else:
            no_data_label = ctk.CTkLabel(self, text="Aucune donnée de classe disponible", font=("Arial", 12))
            no_data_label.grid(row=1, column=1, padx=10, pady=10)


    def __del__(self):
        self.conn_etudiant.close()
        self.conn_enseignant.close()
