import customtkinter as ctk
import sqlite3
from tkinter import messagebox


class ContableTab(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)

        # Database connection
        self.conn_costs = sqlite3.connect("./db/costs_school.db")
        self.cursor_costs = self.conn_costs.cursor()

        # Create table if not exists
        self.cursor_costs.execute('''CREATE TABLE IF NOT EXISTS costs (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        title TEXT,
                                        date TEXT,
                                        costs REAL,
                                        responsible TEXT
                                    )''')
        self.conn_costs.commit()

        # Initialize edit mode variables
        self.edit_mode = False
        self.edit_cost_id = None

        # Configure layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Add/Edit Cost Form
        self.create_add_edit_cost_form()

        # Table Section
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="#CFCFCF",height=400)
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        self.headers = ["Titre", "Date", "Coût", "Responsable", "Actions"]
        for col in range(len(self.headers)):
            self.scrollable_frame.grid_columnconfigure(col, weight=1, minsize=150)

        for col, header in enumerate(self.headers):
            header_label = ctk.CTkLabel(self.scrollable_frame, text=header, font=("Arial", 12, "bold"),
                                        padx=5, pady=5, text_color="white", fg_color="#4285F4")
            header_label.grid(row=0, column=col, sticky="nsew")

        self.display_costs_table()

    def create_add_edit_cost_form(self):
        """Create a form for adding or editing costs."""
        form_frame = ctk.CTkFrame(self, fg_color="#CFCFCF")
        form_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        form_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Input fields
        self.title_entry = ctk.CTkEntry(form_frame, placeholder_text="Titre", width=200)
        self.title_entry.grid(row=0, column=0, padx=5, pady=5)

        self.date_entry = ctk.CTkEntry(form_frame, placeholder_text="Date (YYYY-MM-DD)", width=200)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        self.cost_entry = ctk.CTkEntry(form_frame, placeholder_text="Montant", width=200)
        self.cost_entry.grid(row=0, column=2, padx=5, pady=5)

        self.responsible_entry = ctk.CTkEntry(form_frame, placeholder_text="Responsable", width=200)
        self.responsible_entry.grid(row=0, column=3, padx=5, pady=5)

        # Add/Edit Button
        self.add_edit_button = ctk.CTkButton(form_frame,fg_color="#4285F4", text="Ajouter Coût", command=self.add_or_edit_cost)
        self.add_edit_button.grid(row=0, column=4, padx=5, pady=5)

    def add_or_edit_cost(self):
        """Handles adding a new cost or editing an existing cost."""
        title = self.title_entry.get()
        date = self.date_entry.get()
        costs = self.cost_entry.get()
        responsible = self.responsible_entry.get()

        if title and date and costs and responsible:
            try:
                if self.edit_mode:
                    # Edit existing cost
                    self.cursor_costs.execute(
                        "UPDATE costs SET title = ?, date = ?, costs = ?, responsible = ? WHERE id = ?",
                        (title, date, float(costs), responsible, self.edit_cost_id)
                    )
                    messagebox.showinfo("Succès", "Coût modifié avec succès.")
                else:
                    # Add new cost
                    self.cursor_costs.execute(
                        "INSERT INTO costs (title, date, costs, responsible) VALUES (?, ?, ?, ?)",
                        (title, date, float(costs), responsible)
                    )
                    messagebox.showinfo("Succès", "Coût ajouté avec succès.")

                self.conn_costs.commit()
                self.refresh()

                # Clear form and reset edit mode
                self.reset_form()
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez entrer un montant valide.")
        else:
            messagebox.showerror("Erreur", "Tous les champs doivent être remplis.")

    def reset_form(self):
        """Resets the form to default Add mode."""
        self.title_entry.delete(0, 'end')
        self.date_entry.delete(0, 'end')
        self.cost_entry.delete(0, 'end')
        self.responsible_entry.delete(0, 'end')
        self.edit_mode = False
        self.edit_cost_id = None
        self.add_edit_button.configure(text="Ajouter Coût")

    def display_costs_table(self):
        """Displays the costs in a table."""
        self.cursor_costs.execute("SELECT id, title, date, costs, responsible FROM costs")
        rows = self.cursor_costs.fetchall()

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Re-add headers
        for col, header in enumerate(self.headers):
            header_label = ctk.CTkLabel(self.scrollable_frame, text=header, font=("Arial", 12, "bold"),
                                        padx=5, pady=5, text_color="white", fg_color="#4285F4")
            header_label.grid(row=0, column=col, sticky="nsew")

        for row_index, row in enumerate(rows, start=1):
            for col_index, value in enumerate(row[1:], start=0):
                cost_label = ctk.CTkLabel(self.scrollable_frame, text=str(value), padx=5, pady=5)
                cost_label.grid(row=row_index, column=col_index, sticky="nsew")

            action_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            action_frame.grid(row=row_index, column=len(self.headers) - 1, padx=5, pady=5, sticky="nsew")

            edit_button = ctk.CTkButton(action_frame, width=50, text="Modifier",fg_color="#4285F4",command=lambda r=row: self.prepare_edit_cost(r))
            edit_button.pack(side="left", expand=True, padx=5, pady=5)

            delete_button = ctk.CTkButton(action_frame, width=50, text="Supprimer",fg_color="#4285F4", command=lambda r=row: self.delete_cost(r))
            delete_button.pack(side="right", expand=True, padx=5, pady=5)

    def prepare_edit_cost(self, row):
        """Prepares the form for editing an existing cost."""
        self.edit_mode = True
        self.edit_cost_id = row[0]  # Use the ID of the selected cost

        # Populate form fields with the selected cost's data
        self.title_entry.delete(0, 'end')
        self.title_entry.insert(0, row[1])

        self.date_entry.delete(0, 'end')
        self.date_entry.insert(0, row[2])

        self.cost_entry.delete(0, 'end')
        self.cost_entry.insert(0, row[3])

        self.responsible_entry.delete(0, 'end')
        self.responsible_entry.insert(0, row[4])

        self.add_edit_button.configure(text="Modifier Coût")

    def delete_cost(self, row):
        """Deletes a selected cost."""
        self.cursor_costs.execute("DELETE FROM costs WHERE id = ?", (row[0],))
        self.conn_costs.commit()
        self.refresh()

    def refresh(self):
        """Refreshes the table and resets the form."""
        self.display_costs_table()
        self.reset_form()
