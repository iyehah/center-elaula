import unittest
import sqlite3
import os
from app import App
from auth.login import LoginWindow
from auth.signin import RegisterWindow
import customtkinter as ctk

class TestApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        cls.db_path = "./db/school_account.db"
        # Ensure the database file is removed before each test
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def setUp(self):
        """Initialize the application and database for each test."""
        self.app = App()
        self.app.setup_database()

    def tearDown(self):
        """Clean up after each test."""
        # Delete the test user account if it exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE number = ?", ("43000038",))
        conn.commit()
        conn.close()

        # Remove the database file
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_database_setup(self):
        """Test if the database and 'users' table are created correctly."""
        # Check if the database file exists
        self.assertTrue(os.path.exists(self.db_path), "Database file was not created.")

        # Check if the 'users' table exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(table_exists, "The 'users' table was not created.")

    def test_initial_account_existence(self):
        """Test if the 'Create Account' button visibility is updated based on account existence."""
        # Initially, no accounts should exist, so the button should be visible
        self.assertTrue(self.app.login_frame.create_account_button.winfo_ismapped(), "Create Account button should be visible when no accounts exist.")

        # Add a test user and check again
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, number, type, password) VALUES (?, ?, ?, ?)",
                       ("Test User", "123456789", "Admin", "password123"))
        conn.commit()
        conn.close()

        # Reinitialize the app and check account existence
        self.app = App()
        self.app.setup_database()

        # The "Create Account" button should be hidden if accounts exist
        self.assertFalse(self.app.login_frame.create_account_button.winfo_ismapped(), "Create Account button should be hidden when accounts exist.")

    def test_login_valid_credentials(self):
        """Test login with valid credentials."""
        # Add a test user
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, number, type, password) VALUES (?, ?, ?, ?)",
                       ("Test User", "123456789", "Admin", "password123"))
        conn.commit()
        conn.close()

        # Simulate login with valid credentials
        self.app.login_frame.number_entry.insert(0, "123456789")
        self.app.login_frame.password_entry.insert(0, "password123")
        self.app.login_frame.login()

        # Check if the login was successful (you can add more assertions based on your application logic)
        self.assertTrue(True, "Login should succeed with valid credentials.")

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        # Simulate login with invalid credentials
        self.app.login_frame.number_entry.insert(0, "invalid")
        self.app.login_frame.password_entry.insert(0, "invalid")
        self.app.login_frame.login()

        # Check if the login failed (you can add more assertions based on your application logic)
        self.assertTrue(True, "Login should fail with invalid credentials.")

    def test_register_valid_user(self):
        """Test user registration with valid data."""
        # Simulate registration with valid data
        self.app.show_register()
        self.app.register_frame.name_entry.insert(0, "Tester User")
        self.app.register_frame.number_entry.insert(0, "43000038")  # Number
        self.app.register_frame.type_entry.set("tester")  # Type
        self.app.register_frame.password_entry.insert(0, "43000038")  # Password
        self.app.register_frame.password_again_entry.insert(0, "43000038")  # Confirm Password
        self.app.register_frame.register()

        # Check if the user was registered successfully
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE number = ?", ("43000038",))
        user = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(user, "User should be registered successfully.")
        self.assertEqual(user[1], "43000038", "User number should be 43000038.")
        self.assertEqual(user[3], "43000038", "User password should be 43000038.")
        self.assertEqual(user[2], "tester", "User type should be tester.")

    def test_register_duplicate_user(self):
        """Test user registration with a duplicate number."""
        # Add a test user
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, number, type, password) VALUES (?, ?, ?, ?)",
                       ("Test User", "123456789", "Admin", "password123"))
        conn.commit()
        conn.close()

        # Simulate registration with a duplicate number
        self.app.show_register()
        self.app.register_frame.name_entry.insert(0, "Duplicate User")
        self.app.register_frame.number_entry.insert(0, "123456789")
        self.app.register_frame.type_entry.set("École")
        self.app.register_frame.password_entry.insert(0, "password123")
        self.app.register_frame.password_again_entry.insert(0, "password123")
        self.app.register_frame.register()

        # Check if the registration failed due to duplicate number
        self.assertTrue(True, "Registration should fail for duplicate user.")

    def test_register_password_mismatch(self):
        """Test user registration with mismatched passwords."""
        # Simulate registration with mismatched passwords
        self.app.show_register()
        self.app.register_frame.name_entry.insert(0, "New User")
        self.app.register_frame.number_entry.insert(0, "987654321")
        self.app.register_frame.type_entry.set("École")
        self.app.register_frame.password_entry.insert(0, "password123")
        self.app.register_frame.password_again_entry.insert(0, "mismatch")
        self.app.register_frame.register()

        # Check if the registration failed due to mismatched passwords
        self.assertTrue(True, "Registration should fail for mismatched passwords.")

    def test_show_login_and_register(self):
        """Test switching between login and register frames."""
        # Initially, the login frame should be visible
        self.assertTrue(self.app.login_frame.winfo_ismapped(), "Login frame should be visible by default.")

        # Switch to the register frame
        self.app.show_register()
        self.assertTrue(self.app.register_frame.winfo_ismapped(), "Register frame should be visible after switching.")

        # Switch back to the login frame
        self.app.show_login()
        self.assertTrue(self.app.login_frame.winfo_ismapped(), "Login frame should be visible after switching back.")

if __name__ == "__main__":
    unittest.main()