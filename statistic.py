import customtkinter as ctk
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
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
        """Graphique en camembert : Prix total vs Salaire total avec légende ou message d'absence de données."""

        # Récupérer les données depuis la base de données
        curseur_etudiant = self.conn_etudiant.cursor()
        curseur_etudiant.execute("SELECT SUM(price) FROM students")
        prix_total = curseur_etudiant.fetchone()[0] or 0

        curseur_enseignant = self.conn_enseignant.cursor()
        curseur_enseignant.execute("SELECT SUM(salary) FROM teachers")
        salaire_total = curseur_enseignant.fetchone()[0] or 0

        # Vérifier si les données existent
        if prix_total > 0 or salaire_total > 0:
            # Données disponibles, afficher le graphique en camembert
            labels = ["Prix Total", "Salaire Total"]
            sizes = [prix_total, salaire_total]
            couleurs = ['#4CAF50', '#FF5722']

            fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
            fig.patch.set_facecolor('#CFCFCF')
            wedges, texts, autotexts = ax.pie(
                sizes, labels=labels, autopct='%1.1f%%',
                startangle=140, colors=couleurs, textprops={'color': 'black'}
            )
            ax.set_title("Prix Total vs Salaire Total", fontsize=12, color='black')
            ax.legend(
                loc="upper right", fontsize=8, facecolor='#CFCFCF',
                bbox_to_anchor=(1.5, 0.1)
                
            )
            ax.set_facecolor((0, 0, 0, 0))

            canvas = FigureCanvasTkAgg(fig, master=self)
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        else:
            # Aucune donnée disponible, afficher un message
            no_data_label = ctk.CTkLabel(
                self,
                text="Aucune donnée de paiement étudiant ou enseignant disponible",
                font=("Arial", 12)
            )
            no_data_label.grid(row=0, column=0, padx=10, pady=10)

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
            # Trier les données par date
            sorted_data = sorted(zip(dates, prix), key=lambda x: x[0])
            sorted_dates, sorted_prix = zip(*sorted_data)

            # Créer le graphique
            fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
            fig.patch.set_facecolor('#CFCFCF')
            ax.plot(sorted_dates, sorted_prix, marker='o', linestyle='-', color='#1E90FF')
            ax.set_title("Paiement des Étudiants au Fil du Temps", fontsize=12, color='black')
            ax.set_xlabel("Date", fontsize=8, color='black')
            ax.set_ylabel("Prix", fontsize=8, color='black')
            ax.grid(True, color='black', linewidth=0.2)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('black')
            ax.spines['bottom'].set_linewidth(1)
            ax.spines['left'].set_color('black')
            ax.spines['left'].set_linewidth(1)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            fig.autofmt_xdate()
            ax.tick_params(axis='x', colors='black')  # Couleur des étiquettes de l'axe X
            ax.tick_params(axis='y', colors='black')  # Couleur des étiquettes de l'axe Y
            ax.set_facecolor((0, 0, 0, 0))

            # Ajouter la légende
            mois_actuel = datetime.now().strftime("%B")  # Nom du mois en anglais
            mois_francais = {
                "January": "Janvier", "February": "Février", "March": "Mars", "April": "Avril",
                "May": "Mai", "June": "Juin", "July": "Juillet", "August": "Août",
                "September": "Septembre", "October": "Octobre", "November": "Novembre", "December": "Décembre"
            }
            mois_fr = mois_francais.get(mois_actuel, mois_actuel)  # Traduire en français
            annee_mois = datetime.now().strftime(f"{mois_fr} %Y")
            ax.legend([f"{annee_mois}"],loc='upper right', fontsize=8, facecolor='#CFCFCF', bbox_to_anchor=(1.11, 1.1))
            plt.xticks(rotation=0,fontsize=6, ha="right")
            plt.yticks(fontsize=6)
            # Afficher le graphique dans l'interface Tkinter
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
            fig.patch.set_facecolor('#CFCFCF')
            ax.bar(mois, comptes, color='#FF9900',width=8)
            ax.set_title("Inscriptions des Étudiants par Mois", fontsize=12, color='black')
            ax.set_xlabel("Mois", fontsize=8, color='black')
            ax.set_ylabel("Inscriptions", fontsize=8, color='black')
            ax.grid(True, color='black', linewidth=0.2)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            # Définir la couleur de la bordure inférieure et gauche
            ax.spines['bottom'].set_color('black')
            ax.spines['bottom'].set_linewidth(1)
            ax.spines['left'].set_color('black')
            ax.spines['left'].set_linewidth(1)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m'))
            fig.autofmt_xdate()
            ax.tick_params(axis='x', colors='black')  # Couleur des étiquettes de l'axe X
            ax.tick_params(axis='y', colors='black')  # Couleur des étiquettes de l'axe Y
            ax.set_facecolor((0, 0, 0, 0))
            plt.xticks(rotation=0,fontsize=6, ha="right")
            plt.yticks(fontsize=6)

            canvas = FigureCanvasTkAgg(fig, master=self)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        else:
            no_data_label = ctk.CTkLabel(self, text="Aucune donnée d'inscription disponible", font=("Arial", 12))
            no_data_label.grid(row=1, column=0, padx=10, pady=10)

    def creer_graphique_pourcentages_classes(self): 
            curseur_etudiant = self.conn_etudiant.cursor()

            # Calculate the start and end dates of the current week
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())  # Monday
            end_of_week = start_of_week + timedelta(days=6)  # Sunday

            # Fetch data for this week only
            curseur_etudiant.execute("""
                SELECT class, date_register, COUNT(*) 
                FROM students 
                WHERE date_register BETWEEN ? AND ?
                GROUP BY class, date_register 
                ORDER BY date_register
            """, (start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d')))
            data = curseur_etudiant.fetchall()

            if data:
                # Prepare the data
                classes = set(row[0] for row in data)  # Get all unique classes
                données_classes = {cls: [] for cls in classes}
                dates = sorted(set(row[1] for row in data))  # Get all unique dates for the week

                # Organize the data by class and by date
                for cls in classes:
                    données_classes[cls] = [0] * len(dates)  # Initialize counts with zeros
                    for i, date in enumerate(dates):
                        # Get the count of students for this class on this date
                        count = next((row[2] for row in data if row[0] == cls and row[1] == date), 0)
                        données_classes[cls][i] = count

                # Plot the data
                fig, ax = plt.subplots(figsize=(8, 3), dpi=100)
                fig.patch.set_facecolor('#CFCFCF')

                # Plot each class
                for idx, (cls, counts) in enumerate(données_classes.items()):
                    ax.plot(dates, counts, label=cls, marker='o', color=plt.cm.tab20(idx / len(données_classes)))

                # Format the x-axis with French days
                jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
                ax.set_xticks(range(len(jours)))
                ax.set_xticklabels(jours)

                # Customizing the graph appearance
                ax.grid(True, color='black', linewidth=0.2)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_color('black')
                ax.spines['bottom'].set_linewidth(1)
                ax.spines['left'].set_color('black')
                ax.spines['left'].set_linewidth(1)
                ax.set_xlabel('Jours', fontsize=8, color='black')
                ax.set_ylabel('Nombre d\'Étudiants', fontsize=8, color='black')
                ax.set_title('Étudiants par Classe (Cette Semaine)', fontsize=12, color='black')
                ax.legend(loc='upper right', fontsize=8, facecolor='#CFCFCF', bbox_to_anchor=(1.11, 1.1))
                
                ax.set_facecolor((0, 0, 0, 0))
                plt.xticks(rotation=0,fontsize=6, ha="right")
                plt.yticks(fontsize=6)

                # Embed the graph into tkinter
                canvas = FigureCanvasTkAgg(fig, master=self)
                canvas.draw()
                canvas.get_tk_widget().grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

            else:
                # Display a message if no data is available
                no_data_label = ctk.CTkLabel(self, text="Aucune donnée de classe disponible cette semaine", font=("Arial", 12))
                no_data_label.grid(row=1, column=1, padx=10, pady=10)

    def __del__(self):
        self.conn_etudiant.close()
        self.conn_enseignant.close()
