import csv, time, statistics
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from .models import Student, Course, Professor, LoginUser, grade_from_marks
from .security import encrypt_password, decrypt_password

STUDENT_HEADERS = ["Email_address","First_name","Last_name","Course.id","grades","Marks"]
COURSE_HEADERS  = ["Course_id","Course_name","Description","Credits"]
PROF_HEADERS    = ["Professor_id","Professor_Name","Rank","Course.id"]
LOGIN_HEADERS   = ["User_id","Password","Role"]

class CheckMyGradeDB:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.students: List[Student] = []
        self.courses: List[Course] = []
        self.professors: List[Professor] = []
        self.login_users: List[LoginUser] = []
        self._student_index: Dict[str, int] = {}

    @property
    def student_csv(self): return self.data_dir / "students.csv"
    @property
    def course_csv(self): return self.data_dir / "courses.csv"
    @property
    def professor_csv(self): return self.data_dir / "professors.csv"
    @property
    def login_csv(self): return self.data_dir / "login.csv"

    def _rebuild_index(self):
        self._student_index = {s.email_address: i for i, s in enumerate(self.students)}

    def add_student(self, s: Student):
        if not s.email_address:
            raise ValueError("student email (id) cannot be empty")
        if s.email_address in self._student_index:
            raise ValueError(f"student with email {s.email_address} already exists")
        if s.course_id and not any(c.course_id == s.course_id for c in self.courses):
            pass
        if (not s.grade or s.grade.strip() == "") and s.marks is not None:
            s.grade = grade_from_marks(int(s.marks))
        self.students.append(s)
        self._rebuild_index()

    def delete_student(self, email: str) -> bool:
        idx = self._student_index.get(email)
        if idx is None:
            return False
        self.students.pop(idx)
        self._rebuild_index()
        return True

    def update_student(self, email: str, **updates) -> bool:
        idx = self._student_index.get(email)
        if idx is None:
            return False
        s = self.students[idx]
        for k, v in updates.items():
            if hasattr(s, k):
                setattr(s, k, v)
        if "marks" in updates and updates["marks"] is not None:
            s.grade = grade_from_marks(int(s.marks))
        self.students[idx] = s
        self._rebuild_index()
        return True

    def search_student_linear(self, email: str) -> Tuple[Optional[Student], float]:
        t0 = time.perf_counter()
        for s in self.students:
            if s.email_address == email:
                t1 = time.perf_counter()
                return s, (t1 - t0)
        t1 = time.perf_counter()
        return None, (t1 - t0)

    def search_student_indexed(self, email: str) -> Tuple[Optional[Student], float]:
        t0 = time.perf_counter()
        idx = self._student_index.get(email)
        s = self.students[idx] if idx is not None else None
        t1 = time.perf_counter()
        return s, (t1 - t0)

    def sort_students(self, by: str = "email", ascending: bool = True) -> float:
        key_funcs = {
            "email": lambda s: s.email_address.lower(),
            "marks": lambda s: (s.marks if s.marks is not None else -1),
            "name":  lambda s: (s.last_name.lower(), s.first_name.lower()),
            "grade": lambda s: s.grade
        }
        if by not in key_funcs:
            raise ValueError("by must be one of: " + ", ".join(key_funcs))
        t0 = time.perf_counter()
        self.students.sort(key=key_funcs[by], reverse=not ascending)
        t1 = time.perf_counter()
        self._rebuild_index()
        return (t1 - t0)

    def add_course(self, c: Course):
        if not c.course_id:
            raise ValueError("course_id cannot be empty")
        if any(x.course_id == c.course_id for x in self.courses):
            raise ValueError(f"course {c.course_id} already exists")
        self.courses.append(c)

    def delete_course(self, course_id: str) -> bool:
        for i, c in enumerate(self.courses):
            if c.course_id == course_id:
                self.courses.pop(i)
                return True
        return False

    def update_course(self, course_id: str, **updates) -> bool:
        for i, c in enumerate(self.courses):
            if c.course_id == course_id:
                for k, v in updates.items():
                    if hasattr(c, k):
                        setattr(c, k, v)
                self.courses[i] = c
                return True
        return False

    # ---------- CRUD: Professor ----------
    def add_professor(self, p: Professor):
        if not p.professor_id:
            raise ValueError("professor_id cannot be empty")
        if any(x.professor_id == p.professor_id for x in self.professors):
            raise ValueError(f"professor {p.professor_id} already exists")
        self.professors.append(p)

    def delete_professor(self, professor_id: str) -> bool:
        for i, p in enumerate(self.professors):
            if p.professor_id == professor_id:
                self.professors.pop(i)
                return True
        return False

    def update_professor(self, professor_id: str, **updates) -> bool:
        for i, p in enumerate(self.professors):
            if p.professor_id == professor_id:
                for k, v in updates.items():
                    if hasattr(p, k):
                        setattr(p, k, v)
                self.professors[i] = p
                return True
        return False

    # ---------- Reports / Stats ----------
    def course_stats(self, course_id: str):
        marks = [s.marks for s in self.students if s.course_id == course_id and s.marks is not None]
        if not marks:
            return {"count": 0, "average": None, "median": None}
        return {
            "count": len(marks),
            "average": sum(marks) / len(marks),
            "median": statistics.median(marks)
        }

    def report_course_wise(self, course_id: str):
        return [s for s in self.students if s.course_id == course_id]

    def report_student(self, email: str):
        s, _ = self.search_student_indexed(email)
        return s

    def report_professor_wise(self, professor_id: str):
        taught_courses = [p.course_id for p in self.professors if p.professor_id == professor_id]
        return [s for s in self.students if s.course_id in taught_courses]

    # ---------- CSV I/O ----------
    def save_all(self):
        self.save_students()
        self.save_courses()
        self.save_professors()
        self.save_logins()

    def load_all(self):
        self.load_courses()
        self.load_professors()
        self.load_students()   
        self.load_logins()

    def save_students(self):
        with self.student_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=STUDENT_HEADERS)
            writer.writeheader()
            for s in self.students:
                writer.writerow({
                    "Email_address": s.email_address,
                    "First_name": s.first_name,
                    "Last_name": s.last_name,
                    "Course.id": s.course_id,
                    "grades": s.grade,
                    "Marks": s.marks,
                })

    def load_students(self):
        self.students.clear()
        if not self.student_csv.exists():
            self._rebuild_index()
            return
        with self.student_csv.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                marks = int(row.get("Marks")) if (row.get("Marks","").strip() != "") else None
                grade = row.get("grades", "").strip() or (grade_from_marks(marks) if marks is not None else "")
                s = Student(
                    email_address=row.get("Email_address","").strip(),
                    first_name=row.get("First_name","").strip(),
                    last_name=row.get("Last_name","").strip(),
                    course_id=row.get("Course.id","").strip(),
                    grade=grade,
                    marks=marks if marks is not None else 0
                )
                self.students.append(s)
        self._rebuild_index()

    def save_courses(self):
        with self.course_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COURSE_HEADERS)
            writer.writeheader()
            for c in self.courses:
                writer.writerow({
                    "Course_id": c.course_id,
                    "Course_name": c.course_name,
                    "Description": c.description,
                    "Credits": c.credits
                })

    def load_courses(self):
        self.courses.clear()
        if not self.course_csv.exists():
            return
        with self.course_csv.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                credits = int(row.get("Credits", "3")) if row.get("Credits","").strip() else 3
                c = Course(
                    course_id=row.get("Course_id","").strip(),
                    course_name=row.get("Course_name","").strip(),
                    description=row.get("Description","").strip(),
                    credits=credits
                )
                self.courses.append(c)

    def save_professors(self):
        with self.professor_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=PROF_HEADERS)
            writer.writeheader()
            for p in self.professors:
                writer.writerow({
                    "Professor_id": p.professor_id,
                    "Professor_Name": p.professor_name,
                    "Rank": p.rank,
                    "Course.id": p.course_id
                })

    def load_professors(self):
        self.professors.clear()
        if not self.professor_csv.exists():
            return
        with self.professor_csv.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                p = Professor(
                    professor_id=row.get("Professor_id","").strip(),
                    professor_name=row.get("Professor_Name","").strip(),
                    rank=row.get("Rank","").strip(),
                    course_id=row.get("Course.id","").strip(),
                )
                self.professors.append(p)

    def save_logins(self):
        with self.login_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=LOGIN_HEADERS)
            writer.writeheader()
            for u in self.login_users:
                writer.writerow({
                    "User_id": u.user_id,
                    "Password": u.password,
                    "Role": u.role
                })

    def load_logins(self):
        self.login_users.clear()
        if not self.login_csv.exists():
            return
        with self.login_csv.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                u = LoginUser(
                    user_id=row.get("User_id","").strip(),
                    password=row.get("Password","").strip(),
                    role=row.get("Role","").strip()
                )
                self.login_users.append(u)

    def register_user(self, email: str, password_plain: str, role: str = "student"):
        enc = encrypt_password(password_plain)
        self.login_users.append(LoginUser(user_id=email, password=enc, role=role))

    def login(self, email: str, password_plain: str) -> bool:
        for u in self.login_users:
            if u.user_id == email:
                try:
                    return (password_plain == decrypt_password(u.password))
                except Exception:
                    return False
        return False
