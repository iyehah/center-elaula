import unittest
import sqlite3
import os

class TestSchoolDatabases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        cls.db_dir = "db"  # Directory containing the database files
        cls.db_files = [
            "costs_school.db",
            "school_account.db",
            "student_school.db",
            "teacher_school.db"
        ]

    def test_database_files_exist(self):
        """Test if all database files exist in the db directory."""
        for db_file in self.db_files:
            db_path = os.path.join(self.db_dir, db_file)
            self.assertTrue(os.path.exists(db_path), f"{db_path} does not exist.")

    def test_school_account_db_schema(self):
        """Test the schema of the school_account.db."""
        db_path = os.path.join(self.db_dir, "school_account.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if the 'users' table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone()
        self.assertIsNotNone(table_exists, "The 'users' table does not exist in school_account.db.")

        # Check the columns of the 'users' table
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        expected_columns = [
            ("name", "TEXT"),
            ("number", "TEXT"),
            ("type", "TEXT"),
            ("password", "TEXT")
        ]
        for column in columns:
            self.assertIn((column[1], column[2]), expected_columns, f"Unexpected column: {column[1]}")

        conn.close()

    def test_student_school_db_schema(self):
        """Test the schema of the student_school.db."""
        db_path = os.path.join(self.db_dir, "student_school.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if the 'students' table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
        table_exists = cursor.fetchone()
        self.assertIsNotNone(table_exists, "The 'students' table does not exist in student_school.db.")

        # Check the columns of the 'students' table
        cursor.execute("PRAGMA table_info(students)")
        columns = cursor.fetchall()
        expected_columns = [
            ("id", "INTEGER", 1),  # PRIMARY KEY
            ("name", "TEXT", 0),
            ("gender", "TEXT", 0),
            ("class", "TEXT", 0),
            ("subject", "TEXT", 0),
            ("date_register", "TEXT", 0),
            ("parent_number", "TEXT", 0),
            ("price", "REAL", 0),
            ("date_pay", "TEXT", 0),
            ("discount", "REAL", 0)
        ]
        for column in columns:
            self.assertIn((column[1], column[2], column[5]), expected_columns, f"Unexpected column: {column[1]}")

        conn.close()

    def test_teacher_school_db_schema(self):
        """Test the schema of the teacher_school.db."""
        db_path = os.path.join(self.db_dir, "teacher_school.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if the 'teachers' table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='teachers'")
        table_exists = cursor.fetchone()
        self.assertIsNotNone(table_exists, "The 'teachers' table does not exist in teacher_school.db.")

        # Check the columns of the 'teachers' table
        cursor.execute("PRAGMA table_info(teachers)")
        columns = cursor.fetchall()
        expected_columns = [
            ("id", "INTEGER", 1),  # PRIMARY KEY
            ("name", "TEXT", 0),
            ("class", "TEXT", 0),
            ("subject", "TEXT", 0),
            ("salary", "REAL", 0),
            ("number", "TEXT", 0),
            ("percentage", "REAL", 0)
        ]
        for column in columns:
            self.assertIn((column[1], column[2], column[5]), expected_columns, f"Unexpected column: {column[1]}")

        conn.close()

    def test_costs_school_db_schema(self):
        """Test the schema of the costs_school.db."""
        db_path = os.path.join(self.db_dir, "costs_school.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if the 'costs' table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='costs'")
        table_exists = cursor.fetchone()
        self.assertIsNotNone(table_exists, "The 'costs' table does not exist in costs_school.db.")

        # Check the columns of the 'costs' table
        cursor.execute("PRAGMA table_info(costs)")
        columns = cursor.fetchall()
        expected_columns = [
            ("id", "INTEGER", 1),  # PRIMARY KEY, AUTOINCREMENT
            ("title", "TEXT", 0),
            ("date", "TEXT", 0),
            ("costs", "REAL", 0),
            ("responsible", "TEXT", 0)
        ]
        for column in columns:
            self.assertIn((column[1], column[2], column[5]), expected_columns, f"Unexpected column: {column[1]}")

        conn.close()

if __name__ == "__main__":
    unittest.main()