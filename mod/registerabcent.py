import customtkinter as ctk
import sqlite3
from datetime import datetime
from tkinter import messagebox
import pywhatkit


class RegisterAbcentTab(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)

        # Database connections
        self.student_conn = sqlite3.connect("./db/student_school.db")
        self.student_cursor = self.student_conn.cursor()
        self.user_conn = sqlite3.connect("./db/school_account.db")
        self.user_cursor = self.user_conn.cursor()

        # Main frame layout
        self.pack(fill="both", expand=True)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Content
        self.grid_rowconfigure(2, weight=0)  # Footer
        self.grid_columnconfigure(0, weight=1)

        # Search frame
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.grid(row=0, column=0, pady=10, padx=20, sticky="n")

        # Class filter dropdown
        self.class_filter = ctk.CTkOptionMenu(
            self.search_frame,
            fg_color="white",
            button_color="#4285F4",
            text_color="black",
            width=200,
            values=["Tous", "3As", "4As", "5C", "5D", "6C1", "6C2", "6D", "7C", "7D1", "7D2", "P.E", "S.C", "English", "Français"],
        )
        self.class_filter.set("Tous")
        self.class_filter.grid(row=0, column=1, padx=5, pady=5)

        # Refresh button
        self.refresh_button = ctk.CTkButton(
            self.search_frame,
            text="Refresh",
            command=self.filter_students,
            fg_color="#4285F4",
            text_color="white",
        )
        self.refresh_button.grid(row=0, column=2, padx=5, pady=5)

        # Scrollable frame for student table
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=600, height=400)
        self.scrollable_frame.grid(row=1, column=0, padx=10, pady=10)

        # Dictionary to store selected students
        self.selected_students = {}

        # Send button
        self.send_button = ctk.CTkButton(
            self,
            text="Envoyer",
            command=self.send_messages_to_parents,
            fg_color="#4285F4",
            hover_color="#34A853",
            text_color="white",
        )
        self.send_button.grid(row=2, column=0, pady=10, padx=20)

    def filter_students(self):
        """Filter and display students by class."""
        # Clear previous table
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        selected_class = self.class_filter.get()
        query = "SELECT id, name, class, subject, parent_number FROM students"
        params = ()
        if selected_class != "Tous":
            query += " WHERE class=?"
            params = (selected_class,)

        try:
            self.student_cursor.execute(query, params)
            students = self.student_cursor.fetchall()

            headers = ["Index", "Nom", "Classe", "Matière", "Numéro de parent", "Sélectionner"]
            for col, header in enumerate(headers):
                ctk.CTkLabel(self.scrollable_frame, text=header).grid(row=0, column=col, padx=5, pady=5)

            for i, (student_id, name, student_class, subject, parent_number) in enumerate(students, start=1):
                ctk.CTkLabel(self.scrollable_frame, text=str(i)).grid(row=i, column=0, padx=5, pady=5)
                ctk.CTkLabel(self.scrollable_frame, text=name).grid(row=i, column=1, padx=5, pady=5)
                ctk.CTkLabel(self.scrollable_frame, text=student_class).grid(row=i, column=2, padx=5, pady=5)
                ctk.CTkLabel(self.scrollable_frame, text=subject).grid(row=i, column=3, padx=5, pady=5)
                ctk.CTkLabel(self.scrollable_frame, text=parent_number).grid(row=i, column=4, padx=5, pady=5)

                checkbox = ctk.CTkCheckBox(
                    self.scrollable_frame,
                    text="",
                    command=lambda sid=student_id: self.toggle_student_selection(sid),
                )
                checkbox.grid(row=i, column=5, padx=10)
        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            ctk.CTkLabel(self.scrollable_frame, text="Database Error!").grid(row=1, column=0, columnspan=6, padx=5, pady=5)

    def toggle_student_selection(self, student_id):
        """Toggle student selection."""
        if student_id in self.selected_students:
            del self.selected_students[student_id]
        else:
            try:
                self.student_cursor.execute("SELECT name, parent_number FROM students WHERE id=?", (student_id,))
                student = self.student_cursor.fetchone()
                if student:
                    self.selected_students[student_id] = student
            except sqlite3.Error as e:
                print(f"Database Error: {e}")

    def send_messages_to_parents(self):
        """Send WhatsApp messages to selected students' parents."""
        if not self.selected_students:
            messagebox.showinfo("Info", "No students selected.")
            return

        try:
            self.user_cursor.execute("SELECT name FROM users LIMIT 1")
            center_name = self.user_cursor.fetchone()[0] or "Centre Elaula"
        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            center_name = "Centre Elaula"

        success_count = 0
        failed_count = 0

        for student_id, (name, parent_number) in self.selected_students.items():
            if not parent_number:
                failed_count += 1
                continue

            message = (
                f"نود إبلاغكم بأن التلميذ(ة) *{name}* غاب(ت) اليوم الموافق `{datetime.now().strftime('%Y-%m-%d')}`.\n"
                "> نرجو أن يكون السبب خيرًا.\n\n"
                f"{center_name}"
            )

            try:
                pywhatkit.sendwhatmsg_instantly(f"+{parent_number}", message)
                success_count += 1
            except Exception as e:
                print(f"Failed to send message to {parent_number}: {e}")
                failed_count += 1

        messagebox.showinfo(
            "Results",
            f"Messages sent successfully: {success_count}\nMessages failed: {failed_count}",
        )
