import customtkinter as ctk
import sqlite3
from tkinter import messagebox

class SettingsTab(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)
        
        self.user_id = 1  # Assuming the user's id is 1
        
        # Create widgets to display and update user information
        self.name_label = ctk.CTkLabel(self, text="Name:")
        self.name_label.grid(row=0, column=0, padx=10, pady=5)
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)

        self.number_label = ctk.CTkLabel(self, text="Phone Number:")
        self.number_label.grid(row=1, column=0, padx=10, pady=5)
        self.number_entry = ctk.CTkEntry(self)
        self.number_entry.grid(row=1, column=1, padx=10, pady=5)

        self.type_label = ctk.CTkLabel(self, text="Account Type:")
        self.type_label.grid(row=2, column=0, padx=10, pady=5)
        
        # Dropdown (OptionMenu) for account type selection
        self.type_values = ["École", "Centre"]
        self.type_var = ctk.StringVar(value=self.type_values[0])  # Default value
        self.type_dropdown = ctk.CTkOptionMenu(self, variable=self.type_var, values=self.type_values)
        self.type_dropdown.grid(row=2, column=1, padx=10, pady=5)

        self.password_label = ctk.CTkLabel(self, text="Password:")
        self.password_label.grid(row=3, column=0, padx=10, pady=5)
        self.password_entry = ctk.CTkEntry(self, show="*")
        self.password_entry.grid(row=3, column=1, padx=10, pady=5)

        # Update button
        self.update_button = ctk.CTkButton(self, text="Update", command=self.update_user_info)
        self.update_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    def update_user_info(self):
        # Retrieve user input from entry fields
        new_name = self.name_entry.get()
        new_number = self.number_entry.get()
        new_type = self.type_var.get()  # Get the selected value from the dropdown
        new_password = self.password_entry.get()

        # Validate inputs (you can add more validation as needed)
        if not new_name or not new_number or not new_type or not new_password:
            messagebox.showerror("Error", "All fields must be filled!")
            return

        # Connect to the database and update user information
        try:
            conn = sqlite3.connect("school_account.db")
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET name = ?, number = ?, type = ?, password = ?
                WHERE id = ?
            """, (new_name, new_number, new_type, new_password, self.user_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Your information has been updated successfully!")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

