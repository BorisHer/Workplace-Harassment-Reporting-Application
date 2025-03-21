import sqlite3
from datetime import datetime

# Database Manager
class DatabaseManager:
    def __init__(self, db_name="workplace_harassment.db"):
        self.db_name = db_name
        self.create_tables()

    def connect(self):
        return sqlite3.connect(self.db_name, check_same_thread=False)

    def create_tables(self):
        """Create tables if they don't exist."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    userID INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('Employee', 'HRPersonnel', 'Admin'))
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cases (
                    caseID INTEGER PRIMARY KEY AUTOINCREMENT,
                    reporterID INTEGER,
                    assignedHRID INTEGER,
                    description TEXT NOT NULL,
                    status TEXT CHECK(status IN ('Pending', 'In Review', 'Resolved')) DEFAULT 'Pending',
                    createdAt TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(reporterID) REFERENCES users(userID),
                    FOREIGN KEY(assignedHRID) REFERENCES users(userID)
                )
            ''')
            conn.commit()

    def add_user(self, name, email, password, role):
        """Register a new user."""
        try:
            with self.connect() as conn:
                conn.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                             (name, email, password, role))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False  # Email already exists

    def authenticate_user(self, email, password):
        """Authenticate a user."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
            return cursor.fetchone()  # Returns user record or None

    def report_case(self, reporter_id, description):
        """Employee reports a harassment case."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO cases (reporterID, description) VALUES (?, ?)", (reporter_id, description))
            conn.commit()
            return cursor.lastrowid  # Return the case ID

    def fetch_cases(self, role, user_id=None):
        """Fetch cases based on role."""
        with self.connect() as conn:
            cursor = conn.cursor()
            if role == "HRPersonnel":
                cursor.execute("SELECT * FROM cases WHERE status != 'Resolved'")
            elif role == "Employee":
                cursor.execute("SELECT * FROM cases WHERE reporterID = ?", (user_id,))
            else:  # Admin gets all cases
                cursor.execute("SELECT * FROM cases")
            return cursor.fetchall()

    def update_case_status(self, case_id, new_status, hr_id):
        """HR updates the case status."""
        with self.connect() as conn:
            conn.execute("UPDATE cases SET status = ?, assignedHRID = ? WHERE caseID = ?", (new_status, hr_id, case_id))
            conn.commit()

# Authentication System
class AuthenticationSystem:
    def __init__(self, db):
        self.db = db

    def login(self, email, password):
        user = self.db.authenticate_user(email, password)
        if user:
            print(f"Welcome, {user[1]} ({user[4]})!")
            return user
        else:
            print("Invalid credentials.")
            return None

# Main Execution
if __name__ == "__main__":
    db = DatabaseManager()
    auth_system = AuthenticationSystem(db)

    # Sample Data (For Testing)
    if not db.authenticate_user("employee@example.com", "1234"):
        db.add_user("Alice", "employee@example.com", "1234", "Employee")
    if not db.authenticate_user("hr@example.com", "admin"):
        db.add_user("Bob", "hr@example.com", "admin", "HRPersonnel")
    if not db.authenticate_user("admin@example.com", "admin"):
        db.add_user("Charlie", "admin@example.com", "admin", "Admin")

    # Interactive CLI
    while True:
        user = None
        while not user:
            email = input("Enter your email: ")
            password = input("Enter your password: ")
            user = auth_system.login(email, password)

        role = user[4]  # Extract user role

        while True:
            if role == "Employee":
                print("\n1. Report a Harassment Case\n2. View My Cases\n3. Logout")
                choice = input("Enter your choice: ")
                if choice == "1":
                    description = input("Enter case description: ")
                    case_id = db.report_case(user[0], description)
                    print(f"Case #{case_id} reported successfully.")
                elif choice == "2":
                    cases = db.fetch_cases("Employee", user[0])
                    print("Your Cases:")
                    for case in cases:
                        print(case)
                elif choice == "3":
                    print("Logging out...")
                    break

            elif role == "HRPersonnel":
                print("\n1. View Cases\n2. Update Case Status\n3. Logout")
                choice = input("Enter your choice: ")
                if choice == "1":
                    cases = db.fetch_cases("HRPersonnel")
                    print("Pending Cases:")
                    for case in cases:
                        print(case)
                elif choice == "2":
                    case_id = input("Enter Case ID to update: ")
                    new_status = input("Enter new status (In Review / Resolved): ")
                    db.update_case_status(case_id, new_status, user[0])
                    print("Case updated successfully.")
                elif choice == "3":
                    print("Logging out...")
                    break

            elif role == "Admin":
                print("\n1. View All Cases\n2. Logout")
                choice = input("Enter your choice: ")
                if choice == "1":
                    cases = db.fetch_cases("Admin")
                    print("All Cases:")
                    for case in cases:
                        print(case)
                elif choice == "2":
                    print("Logging out...")
                    break
