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
            query = "SELECT * FROM cases"
            params = ()
            if role == "HRPersonnel":
                query += " WHERE status != 'Resolved'"
            elif role == "Employee":
                query += " WHERE reporterID = ?"
                params = (user_id,)
            cursor.execute(query, params)
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
            role = user[4]
            print(f"\n✅ Welcome, {user[1]} ({role})!\n")
            return user
        else:
            print("❌ Invalid credentials. Please try again.")
            return None

# Utility Function
def display_cases(cases):
    """Formatted case display."""
    if not cases:
        print("No cases found.")
        return
    print("\n📂 Case List:")
    print("=" * 50)
    for case in cases:
        print(f"🆔 Case ID: {case[0]} | Status: {case[4]}")
        print(f"📝 Description: {case[3]}")
        print(f"📅 Reported On: {case[5]}")
        print("-" * 50)

# Main Execution
if __name__ == "__main__":
    print("""
    ==============================================
    🏢 WORKPLACE HARASSMENT REPORTING SYSTEM 🏢
    ==============================================
    Welcome! Please log in to continue.
    """)
    
    db = DatabaseManager()
    auth_system = AuthenticationSystem(db)

    while True:
        try:
            user = None
            while not user:
                email = input("📧 Enter your email: ").strip()
                password = input("🔑 Enter your password: ").strip()
                user = auth_system.login(email, password)
            role = user[4]

            while True:
                try:
                    if role == "Employee":
                        print("\n1️⃣ Report a Harassment Case\n2️⃣ View My Cases\n3️⃣ Logout")
                        choice = input("🔹 Enter your choice: ").strip()
                        if choice == "1":
                            description = input("📝 Enter case description: ").strip()
                            if description:
                                case_id = db.report_case(user[0], description)
                                print(f"✅ Case #{case_id} reported successfully.")
                        elif choice == "2":
                            display_cases(db.fetch_cases("Employee", user[0]))
                        elif choice == "3":
                            print("👋 Logging out...")
                            break
                        else:
                            print("❌ Invalid choice. Try again.")

                    elif role == "HRPersonnel":
                        print("\n1️⃣ View Cases\n2️⃣ Update Case Status\n3️⃣ Logout")
                        choice = input("🔹 Enter your choice: ").strip()
                        if choice == "1":
                            display_cases(db.fetch_cases("HRPersonnel"))
                        elif choice == "2":
                            case_id = input("🆔 Enter Case ID: ").strip()
                            new_status = input("🔄 Enter new status (In Review / Resolved): ").strip()
                            if new_status in ["In Review", "Resolved"]:
                                db.update_case_status(case_id, new_status, user[0])
                                print("✅ Case updated successfully.")
                        elif choice == "3":
                            print("👋 Logging out...")
                            break
                        else:
                            print("❌ Invalid choice. Try again.")

                    elif role == "Admin":
                        print("\n1️⃣ View All Cases\n2️⃣ Logout")
                        choice = input("🔹 Enter your choice: ").strip()
                        if choice == "1":
                            display_cases(db.fetch_cases("Admin"))
                        elif choice == "2":
                            print("👋 Logging out...")
                            break
                        else:
                            print("❌ Invalid choice. Try again.")
                except Exception as e:
                    print(f"⚠️ An error occurred: {e}")
        except Exception as e:
            print(f"⚠️ An error occurred: {e}")
