# El Mosaeid

**El Mosaeid** is a desktop application designed to facilitate the management of schools and their resources. It provides tools for handling student and teacher information, financial records, attendance tracking, and more. This application aims to streamline administrative processes and enhance productivity in educational institutions.

---

## Features

- **User Authentication**: Secure login and registration for authorized users.
- **Student and Teacher Management**: Add, update, and manage details for students and teachers.
- **Attendance Tracking**: Monitor and manage attendance records.
- **Financial Management**: Handle payments, non-payments, and other financial activities.
- **Dashboard**: An intuitive dashboard summarizing school activities and statistics.
- **Reports**: Generate detailed reports for various aspects of school operations.

---

## Project Structure Now

```plaintext
Project/
├── .git/
├── __pycache__/
├── Amiri-Regular.ttf             # Font used in the application
├── app.exe                       # Compiled executable for the application
├── app.spec                      # Build specification for PyInstaller
├── absent.py                     # Attendance management logic
├── app.py                        # Main entry point of the application
├── contable.py                   # Module for handling accounts
├── costs_school.db               # Database for school expenses
├── cotisations.py                # Module for handling contributions
├── dashboard.py                  # Dashboard interface
├── dev.png                       # Development-related resources
├── developer.py                  # Developer-specific configurations
├── financial.py                  # Financial management logic
├── general.py                    # General utility functions
├── header.jpg                    # Header image for the interface
├── icon.png                      # Application icon
├── insert.py                     # Insert records into the database
├── login.py                      # Login functionality
├── logo.ico                      # Application logo
├── logo.png                      # Image used for branding
├── mainlayout.py                 # Main layout design
├── nonpay.py                     # Handle non-payment scenarios
├── payment.py                    # Payment management
├── PyWhatKit_DB.txt              # Text file related to PyWhatKit usage
├── registerabcent.py             # Module for registering absentees
├── reports.py                    # Generate reports
├── school_account.db             # Database for school accounts
├── signin.py                     # Sign-in functionality
├── statistic.py                  # Statistical data and analytics
├── student.py                    # Manage student information
├── student_school.db             # Database for student records
├── teacher.py                    # Manage teacher information
├── teacher_school.db             # Database for teacher records
├── topsection.py                 # Top section of the interface
```

---

## After Organizing It Will Look Like This

```plaintext
El Mosaeid/
├── .git/                          # Version control
├── __pycache__/                   # Python cache files
├── assets/                        # Static assets
│   ├── fonts/
│   │   └── Amiri-Regular.ttf
│   ├── images/
│   │   ├── header.jpg
│   │   ├── icon.png
│   │   ├── logo.ico
│   │   └── logo.png
│   └── dev.png
├── databases/                     # Database files
│   ├── costs_school.db
│   ├── school_account.db
│   ├── student_school.db
│   └── teacher_school.db
├── docs/                          # Documentation or related files
│   └── PyWhatKit_DB.txt
├── src/                           # Source code
│   ├── core/                      # Core functionality modules
│   │   ├── app.py
│   │   ├── developer.py
│   │   ├── general.py
│   │   └── mainlayout.py
│   ├── features/                  # Specific features of the app
│   │   ├── absent.py
│   │   ├── contable.py
│   │   ├── cotisations.py
│   │   ├── financial.py
│   │   ├── insert.py
│   │   ├── nonpay.py
│   │   ├── payment.py
│   │   ├── registerabcent.py
│   │   ├── reports.py
│   │   ├── signin.py
│   │   ├── statistic.py
│   │   ├── student.py
│   │   └── teacher.py
│   ├── interfaces/                # GUI or interface modules
│   │   ├── dashboard.py
│   │   ├── login.py
│   │   └── topsection.py
├── build/                         # Build output (e.g., compiled executable)
│   ├── app.exe
│   └── app.spec
```

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/iyehah/Mosaeid.git
   cd Mosaeid
   ```
2. Install dependencies (if any):
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```

---

## Requirements

- **Python 3.x**
- **Dependencies**: Install the necessary libraries using `requirements.txt`.

---

## Screenshots

(Include screenshots of the application interface here.)

---

## Contributing

Contributions are welcome! If you'd like to contribute, please fork the repository and submit a pull request. For major changes, please open an issue first to discuss your proposed changes.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact

Developed by: **[iyehah](https://github.com/iyehah)**  
For inquiries, please contact: **[iyehah@gmail.com]**

