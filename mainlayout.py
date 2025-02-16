import customtkinter as ctk
import sqlite3

class MainLayout(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)

        # Database connections
        self.conn_students = sqlite3.connect("./db/student_school.db")
        self.cursor_students = self.conn_students.cursor()

        self.conn_teachers = sqlite3.connect("./db/teacher_school.db")
        self.cursor_teachers = self.conn_teachers.cursor()

        self.conn_costs = sqlite3.connect("./db/costs_school.db")
        self.cursor_costs = self.conn_costs.cursor()

        # Calculate totals
        total_students = self.get_total_students()
        total_teachers = self.get_total_teachers()
        total_classes = self.get_total_classes()
        total_paid = self.get_total_paid()
        total_unpaid = self.get_total_unpaid()
        students_with_discount = self.get_students_with_discount()

        # Create the main layout with calculated data
        self.create_main_layout(total_students, total_teachers, total_classes, total_paid, total_unpaid, students_with_discount)

    def create_main_layout(self, total_students, total_teachers, total_classes, total_paid, total_unpaid, students_with_discount):
        """Create the main layout with two frames: summary and recent students."""
        main_frame = ctk.CTkFrame(self ,height=400)
        main_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        # Define grid columns with specific weights for equal space distribution
        main_frame.grid_columnconfigure(0, weight=1)  # Left frame takes 1/2 width
        main_frame.grid_columnconfigure(1, weight=1)  # Right frame takes 1/2 width

        # Create the left frame with summary cards
        left_frame = ctk.CTkFrame(main_frame, fg_color="#CFCFCF")
        left_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")  # Padding for spacing
        self.create_summary_cards(left_frame, total_students, total_teachers, total_classes, total_paid, total_unpaid, students_with_discount)

        # Create the right frame with recent students
        right_frame = ctk.CTkFrame(main_frame, fg_color="#CFCFCF")
        right_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")  # Padding for spacing
        self.create_recent_students_list(right_frame)

    def create_summary_cards(self, parent, total_students, total_teachers, total_classes, total_paid, total_unpaid, students_with_discount):
        """Create summary cards."""
        summary_data = [
                {"title": "Nombre total d'élèves", "value": total_students, "color": "#6A1B9A"},
                {"title": "Nombre total d'enseignants", "value": total_teachers, "color": "#00838F"},
                {"title": "Nombre total de classes", "value": total_classes, "color": "#FF5722"},
                {"title": "Total payé", "value": total_paid, "color": "#607D8B"},
                {"title": "Total non payé", "value": total_unpaid, "color": "#F44336"},
                {"title": "Nombre d'étudiants endettés", "value": students_with_discount, "color": "#9C27B0"}
            ]



        # Create cards in a 2-column layout
        for index, data in enumerate(summary_data):
            row, column = divmod(index, 2)
            card = ctk.CTkFrame(parent, corner_radius=10, fg_color=data["color"], height=100)
            card.grid(row=row, column=column, padx=10, pady=10, sticky="ew")

            title_label = ctk.CTkLabel(card, text=data["title"],width=200, font=ctk.CTkFont(size=14, weight="bold"), text_color="white")
            title_label.pack(pady=(10, 0))

            value_label = ctk.CTkLabel(card, text=str(data["value"]), font=ctk.CTkFont(size=20, weight="bold"), text_color="white")
            value_label.pack(pady=(5, 10))

    def create_recent_students_list(self, parent):
        """Create a list displaying recently registered students."""

        # Scrollable frame for student list
        student_list_frame = ctk.CTkScrollableFrame(parent, height=300,width=500)
        student_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Fetch recent students from the database
        recent_students = self.get_recent_students()

        # Add each student as a styled entry
        for student in recent_students:
            student_name, student_class, registration_date = student

            # Create a frame for each student
            student_entry = ctk.CTkFrame(student_list_frame, corner_radius=8, fg_color="#f5f5f5", height=50)
            student_entry.pack(fill="x", padx=10, pady=5)

            # Display student name
            name_label = ctk.CTkLabel(
                student_entry, 
                text=student_name, 
                font=ctk.CTkFont(size=14, weight="bold"), 
                text_color="black"
            )
            name_label.grid(row=0, column=0, sticky="w", padx=(10, 5))

            # Display student class
            class_label = ctk.CTkLabel(
                student_entry, 
                text=f"Class: {student_class}", 
                font=ctk.CTkFont(size=12), 
                text_color="gray"
            )
            class_label.grid(row=0, column=1, sticky="w", padx=(5, 10))

            # Display registration date
            date_label = ctk.CTkLabel(
                student_entry, 
                text=f"Registered: {registration_date}", 
                font=ctk.CTkFont(size=10), 
                text_color="#777777"
            )
            date_label.grid(row=0, column=2, sticky="e", padx=10)

            student_list_frame.update_idletasks()

    # Database query methods
    def get_total_students(self):
        """Obtenir le nombre total d'étudiants."""
        try:
            self.cursor_students.execute("SELECT COUNT(*) FROM students")
            result = self.cursor_students.fetchone()
            return result[0] if result else 0
        except sqlite3.OperationalError as e:
            print(f"Erreur SQL (get_total_students) : {e}")
            return 0

    def get_total_teachers(self):
        """Obtenir le nombre total d'enseignants."""
        try:
            self.cursor_teachers.execute("SELECT COUNT(*) FROM teachers")
            result = self.cursor_teachers.fetchone()
            return result[0] if result else 0
        except sqlite3.OperationalError as e:
            print(f"Erreur SQL (get_total_teachers) : {e}")
            return 0

    def get_total_classes(self):
        """Obtenir le nombre total de classes uniques."""
        try:
            self.cursor_students.execute("SELECT COUNT(DISTINCT class) FROM students")
            result = self.cursor_students.fetchone()
            return result[0] if result else 0
        except sqlite3.OperationalError as e:
            print(f"Erreur SQL (get_total_classes) : {e}")
            return 0

    def get_total_paid(self):
        """Obtenir le nombre d'étudiants ayant payé un prix supérieur à 0."""
        try:
            self.cursor_students.execute("SELECT COUNT(*) FROM students WHERE price > 0")
            result = self.cursor_students.fetchone()
            return result[0] if result else 0
        except sqlite3.OperationalError as e:
            print(f"Erreur SQL (get_total_paid) : {e}")
            return 0

    def get_total_unpaid(self):
        """Obtenir le nombre d'étudiants n'ayant pas payé ou ayant un prix <= 0."""
        try:
            self.cursor_students.execute("SELECT COUNT(*) FROM students WHERE price <= 0")
            result = self.cursor_students.fetchone()
            return result[0] if result else 0
        except sqlite3.OperationalError as e:
            print(f"Erreur SQL (get_total_unpaid) : {e}")
            return 0

    def get_students_with_discount(self):
        """Obtenir le nombre d'étudiants ayant une réduction."""
        try:
            self.cursor_students.execute("SELECT COUNT(*) FROM students WHERE discount > 0")
            result = self.cursor_students.fetchone()
            return result[0] if result else 0
        except sqlite3.OperationalError as e:
            print(f"Erreur SQL (get_students_with_discount) : {e}")
            return 0

    def get_recent_students(self):
        """Obtenir les 7 derniers étudiants inscrits."""
        try:
            self.cursor_students.execute(
                "SELECT name, class, date_register FROM students ORDER BY date_register DESC LIMIT 7"
            )
            return self.cursor_students.fetchall()
        except sqlite3.OperationalError as e:
            print(f"Erreur SQL (get_recent_students) : {e}")
            return []
