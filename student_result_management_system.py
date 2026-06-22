import sqlite3
from pathlib import Path
from tkinter import BOTH, END, LEFT, RIGHT, W, X, Y, StringVar, Tk, Toplevel, messagebox
from tkinter import ttk


APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "student_result.db"


class Database:
    def __init__(self, path=DB_PATH):
        self.path = path
        self.create_tables()

    def connect(self):
        return sqlite3.connect(self.path)

    def create_tables(self):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    duration TEXT NOT NULL,
                    charges TEXT NOT NULL,
                    description TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    roll TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT,
                    gender TEXT,
                    dob TEXT,
                    contact TEXT,
                    admission TEXT,
                    course TEXT,
                    address TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    roll TEXT NOT NULL,
                    name TEXT NOT NULL,
                    course TEXT NOT NULL,
                    marks_obtained REAL NOT NULL,
                    full_marks REAL NOT NULL,
                    percentage REAL NOT NULL,
                    grade TEXT NOT NULL,
                    UNIQUE(roll, course),
                    FOREIGN KEY(roll) REFERENCES students(roll)
                )
                """
            )

    def fetch_all(self, table):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM {table}")
            return cur.fetchall()

    def count(self, table):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            return cur.fetchone()[0]


class StudentResultApp:
    def __init__(self, root):
        self.root = root
        self.db = Database()
        self.root.title("Student Result Management System")
        self.root.geometry("1180x720")
        self.root.minsize(1050, 650)
        self.root.configure(bg="#f5f7fb")
        self.build_layout()
        self.show_dashboard()

    def clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def build_layout(self):
        top = ttk.Frame(self.root, padding=(18, 14))
        top.pack(fill=X)

        title = ttk.Label(top, text="Student Result Management System", font=("Arial", 22, "bold"))
        title.pack(side=LEFT)

        exit_btn = ttk.Button(top, text="Exit", command=self.root.destroy)
        exit_btn.pack(side=RIGHT)

        body = ttk.Frame(self.root)
        body.pack(fill=BOTH, expand=True, padx=18, pady=(0, 18))

        nav = ttk.Frame(body, padding=10)
        nav.pack(side=LEFT, fill=Y)

        buttons = [
            ("Dashboard", self.show_dashboard),
            ("Courses", self.show_courses),
            ("Students", self.show_students),
            ("Results", self.show_results),
            ("Search Result", self.show_search),
        ]
        for text, command in buttons:
            btn = ttk.Button(nav, text=text, command=command)
            btn.pack(fill=X, pady=6, ipady=6)

        self.content = ttk.Frame(body, padding=16)
        self.content.pack(side=RIGHT, fill=BOTH, expand=True)

    def section_title(self, text):
        label = ttk.Label(self.content, text=text, font=("Arial", 18, "bold"))
        label.pack(anchor=W, pady=(0, 14))

    def dashboard_card(self, parent, title, value):
        frame = ttk.LabelFrame(parent, text=title, padding=20)
        frame.pack(side=LEFT, fill=BOTH, expand=True, padx=8)
        ttk.Label(frame, text=str(value), font=("Arial", 26, "bold")).pack()

    def show_dashboard(self):
        self.clear_content()
        self.section_title("Dashboard")
        cards = ttk.Frame(self.content)
        cards.pack(fill=X)
        self.dashboard_card(cards, "Total Courses", self.db.count("courses"))
        self.dashboard_card(cards, "Total Students", self.db.count("students"))
        self.dashboard_card(cards, "Total Results", self.db.count("results"))

        note = ttk.Label(
            self.content,
            text="Use the menu on the left to add courses, register students, enter marks, and search results.",
            font=("Arial", 11),
        )
        note.pack(anchor=W, pady=24)

    def make_form(self, fields):
        form = ttk.Frame(self.content)
        form.pack(fill=X, pady=(0, 12))
        variables = {}
        for index, field in enumerate(fields):
            ttk.Label(form, text=field).grid(row=index // 2, column=(index % 2) * 2, sticky=W, padx=6, pady=6)
            var = StringVar()
            entry = ttk.Entry(form, textvariable=var, width=34)
            entry.grid(row=index // 2, column=(index % 2) * 2 + 1, sticky=W, padx=6, pady=6)
            variables[field] = var
        return variables

    def make_tree(self, columns):
        tree = ttk.Treeview(self.content, columns=columns, show="headings", height=12)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor=W)
        tree.pack(fill=BOTH, expand=True, pady=(10, 0))
        return tree

    def show_courses(self):
        self.clear_content()
        self.section_title("Manage Courses")
        fields = ["Name", "Duration", "Charges", "Description"]
        variables = self.make_form(fields)

        actions = ttk.Frame(self.content)
        actions.pack(fill=X)

        columns = ["ID", "Name", "Duration", "Charges", "Description"]
        tree = self.make_tree(columns)

        def refresh():
            tree.delete(*tree.get_children())
            for row in self.db.fetch_all("courses"):
                tree.insert("", END, values=row)

        def add_course():
            values = [variables[field].get().strip() for field in fields]
            if not values[0] or not values[1] or not values[2]:
                messagebox.showerror("Error", "Name, duration, and charges are required.")
                return
            try:
                with self.db.connect() as con:
                    con.execute(
                        "INSERT INTO courses(name, duration, charges, description) VALUES (?, ?, ?, ?)",
                        values,
                    )
                for var in variables.values():
                    var.set("")
                refresh()
                self.show_dashboard()
                self.show_courses()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "This course already exists.")

        ttk.Button(actions, text="Add Course", command=add_course).pack(side=LEFT, padx=6)
        refresh()

    def show_students(self):
        self.clear_content()
        self.section_title("Manage Students")
        fields = ["Roll", "Name", "Email", "Gender", "DOB", "Contact", "Admission", "Course", "Address"]
        variables = self.make_form(fields)

        actions = ttk.Frame(self.content)
        actions.pack(fill=X)

        columns = ["Roll", "Name", "Email", "Gender", "DOB", "Contact", "Admission", "Course", "Address"]
        tree = self.make_tree(columns)

        def refresh():
            tree.delete(*tree.get_children())
            for row in self.db.fetch_all("students"):
                tree.insert("", END, values=row)

        def add_student():
            values = [variables[field].get().strip() for field in fields]
            if not values[0] or not values[1]:
                messagebox.showerror("Error", "Roll and name are required.")
                return
            try:
                with self.db.connect() as con:
                    con.execute(
                        """
                        INSERT INTO students
                        (roll, name, email, gender, dob, contact, admission, course, address)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        values,
                    )
                for var in variables.values():
                    var.set("")
                refresh()
                self.show_students()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "This roll number already exists.")

        ttk.Button(actions, text="Add Student", command=add_student).pack(side=LEFT, padx=6)
        refresh()

    def grade_from_percentage(self, percentage):
        if percentage >= 80:
            return "A+"
        if percentage >= 70:
            return "A"
        if percentage >= 60:
            return "B"
        if percentage >= 50:
            return "C"
        if percentage >= 40:
            return "D"
        return "F"

    def show_results(self):
        self.clear_content()
        self.section_title("Manage Results")
        fields = ["Roll", "Name", "Course", "Marks Obtained", "Full Marks"]
        variables = self.make_form(fields)

        actions = ttk.Frame(self.content)
        actions.pack(fill=X)

        columns = ["ID", "Roll", "Name", "Course", "Marks", "Full Marks", "Percentage", "Grade"]
        tree = self.make_tree(columns)

        def refresh():
            tree.delete(*tree.get_children())
            for row in self.db.fetch_all("results"):
                tree.insert("", END, values=row)

        def load_student_name():
            roll = variables["Roll"].get().strip()
            if not roll:
                return
            with self.db.connect() as con:
                cur = con.cursor()
                cur.execute("SELECT name, course FROM students WHERE roll=?", (roll,))
                row = cur.fetchone()
            if row:
                variables["Name"].set(row[0])
                variables["Course"].set(row[1])
            else:
                messagebox.showinfo("Not found", "No student found with that roll number.")

        def add_result():
            try:
                marks = float(variables["Marks Obtained"].get().strip())
                full_marks = float(variables["Full Marks"].get().strip())
                if full_marks <= 0 or marks < 0 or marks > full_marks:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Enter valid marks and full marks.")
                return

            roll = variables["Roll"].get().strip()
            name = variables["Name"].get().strip()
            course = variables["Course"].get().strip()
            if not roll or not name or not course:
                messagebox.showerror("Error", "Roll, name, and course are required.")
                return

            percentage = round((marks / full_marks) * 100, 2)
            grade = self.grade_from_percentage(percentage)
            try:
                with self.db.connect() as con:
                    con.execute(
                        """
                        INSERT INTO results
                        (roll, name, course, marks_obtained, full_marks, percentage, grade)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (roll, name, course, marks, full_marks, percentage, grade),
                    )
                for var in variables.values():
                    var.set("")
                refresh()
                self.show_results()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "A result for this student and course already exists.")

        ttk.Button(actions, text="Load Student", command=load_student_name).pack(side=LEFT, padx=6)
        ttk.Button(actions, text="Add Result", command=add_result).pack(side=LEFT, padx=6)
        refresh()

    def show_search(self):
        self.clear_content()
        self.section_title("Search Student Result")
        search_frame = ttk.Frame(self.content)
        search_frame.pack(fill=X, pady=(0, 12))

        ttk.Label(search_frame, text="Roll Number").pack(side=LEFT, padx=(0, 8))
        roll_var = StringVar()
        ttk.Entry(search_frame, textvariable=roll_var, width=30).pack(side=LEFT, padx=(0, 8))

        columns = ["Roll", "Name", "Course", "Marks", "Full Marks", "Percentage", "Grade"]
        tree = self.make_tree(columns)

        def search():
            tree.delete(*tree.get_children())
            roll = roll_var.get().strip()
            if not roll:
                messagebox.showerror("Error", "Enter a roll number.")
                return
            with self.db.connect() as con:
                cur = con.cursor()
                cur.execute(
                    """
                    SELECT roll, name, course, marks_obtained, full_marks, percentage, grade
                    FROM results WHERE roll=?
                    """,
                    (roll,),
                )
                rows = cur.fetchall()
            if not rows:
                messagebox.showinfo("No result", "No result found for this roll number.")
            for row in rows:
                tree.insert("", END, values=row)

        ttk.Button(search_frame, text="Search", command=search).pack(side=LEFT)


def main():
    root = Tk()
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TButton", font=("Arial", 11), padding=6)
    style.configure("TLabel", font=("Arial", 10))
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
    StudentResultApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
