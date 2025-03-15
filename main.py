from datetime import datetime

# Base User class
class User:
    def __init__(self, user_id, name, email, password):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password

    def login(self):
        print(f"{self.name} logged in")

    def logout(self):
        print(f"{self.name} logged out")

# Employee class (inherits from User)
class Employee(User):
    def report_harassment(self, description):
        new_case = Case(case_id=len(Case.cases) + 1, reporter=self, description=description)
        Case.cases.append(new_case)
        print(f"Harassment case reported by {self.name}")
        return new_case

    def view_case_status(self, case_id):
        for case in Case.cases:
            if case.case_id == case_id and case.reporter == self:
                return case.status
        return "Case not found"

# HRPersonnel class (inherits from User)
class HRPersonnel(User):
    def review_case(self, case_id):
        case = self._find_case(case_id)
        if case:
            print(f"HR {self.name} is reviewing case {case_id}")
    
    def resolve_case(self, case_id, resolution):
        case = self._find_case(case_id)
        if case:
            case.status = "Resolved"
            print(f"Case {case_id} resolved with resolution: {resolution}")

    def communicate_with_employee(self, employee_id, message):
        print(f"HR {self.name} sent a message to Employee {employee_id}: {message}")

    def _find_case(self, case_id):
        for case in Case.cases:
            if case.case_id == case_id and case.assigned_hr == self:
                return case
        return None

# Admin class (inherits from User)
class Admin(User):
    def oversee_cases(self):
        return [case for case in Case.cases]

    def ensure_compliance(self):
        print("Admin is ensuring compliance with workplace policies")

# Case class to handle reported cases
class Case:
    cases = []

    def __init__(self, case_id, reporter, description):
        self.case_id = case_id
        self.reporter = reporter
        self.assigned_hr = None  # Will be assigned later
        self.description = description
        self.status = "Pending"
        self.created_at = datetime.now()

    def update_status(self, new_status):
        self.status = new_status

# Authentication System
class AuthenticationSystem:
    users = {}

    @staticmethod
    def authenticate_user(email, password):
        user = AuthenticationSystem.users.get(email)
        if user and user.password == password:
            print(f"Authentication successful for {user.name}")
            return user
        else:
            print("Authentication failed")
            return None

    @staticmethod
    def logout_user(user):
        print(f"{user.name} has logged out")

# Interactive CLI Application
def main():
    # Sample users
    emp = Employee(1, "Alice", "alice@example.com", "password123")
    hr = HRPersonnel(2, "Bob", "bob@example.com", "password456")
    admin = Admin(3, "Charlie", "charlie@example.com", "adminpass")
    
    AuthenticationSystem.users[emp.email] = emp
    AuthenticationSystem.users[hr.email] = hr
    AuthenticationSystem.users[admin.email] = admin

    while True:
        email = input("Enter email: ")
        password = input("Enter password: ")
        user = AuthenticationSystem.authenticate_user(email, password)
        if user:
            while True:
                if isinstance(user, Employee):
                    print("1. Report Harassment")
                    print("2. View Case Status")
                    print("3. Logout")
                    choice = input("Choose an option: ")
                    if choice == "1":
                        desc = input("Enter case description: ")
                        user.report_harassment(desc)
                    elif choice == "2":
                        case_id = int(input("Enter case ID: "))
                        print("Case Status:", user.view_case_status(case_id))
                    elif choice == "3":
                        AuthenticationSystem.logout_user(user)
                        break
                elif isinstance(user, HRPersonnel):
                    print("1. Review Case")
                    print("2. Resolve Case")
                    print("3. Logout")
                    choice = input("Choose an option: ")
                    if choice == "1":
                        case_id = int(input("Enter case ID: "))
                        user.review_case(case_id)
                    elif choice == "2":
                        case_id = int(input("Enter case ID: "))
                        resolution = input("Enter resolution: ")
                        user.resolve_case(case_id, resolution)
                    elif choice == "3":
                        AuthenticationSystem.logout_user(user)
                        break
                elif isinstance(user, Admin):
                    print("1. Oversee Cases")
                    print("2. Ensure Compliance")
                    print("3. Logout")
                    choice = input("Choose an option: ")
                    if choice == "1":
                        cases = user.oversee_cases()
                        for case in cases:
                            print(f"Case {case.case_id}: {case.description} - Status: {case.status}")
                    elif choice == "2":
                        user.ensure_compliance()
                    elif choice == "3":
                        AuthenticationSystem.logout_user(user)
                        break
        else:
            print("Invalid credentials, try again!")

if __name__ == "__main__":
    main()
