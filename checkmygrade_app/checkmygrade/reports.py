from typing import List
from .models import Student
from .storage import CheckMyGradeDB

def print_student(s: Student) -> str:
    return f"{s.email_address:25s} | {s.first_name:10s} {s.last_name:12s} | {s.course_id:8s} | {s.grade:3s} | {s.marks:3d}"

def render_course_report(db: CheckMyGradeDB, course_id: str) -> str:
    rows = [print_student(s) for s in db.report_course_wise(course_id)]
    header = "Email                     | Name                 | Course   | Grd | Mk"
    return "\n".join([header, "-"*len(header)] + rows)

def render_professor_report(db: CheckMyGradeDB, professor_id: str) -> str:
    rows = [print_student(s) for s in db.report_professor_wise(professor_id)]
    header = "Email                     | Name                 | Course   | Grd | Mk"
    return "\n".join([header, "-"*len(header)] + rows)

def render_student_report(db: CheckMyGradeDB, email: str) -> str:
    s = db.report_student(email)
    if not s:
        return "Student not found."
    header = "Email                     | Name                 | Course   | Grd | Mk"
    return "\n".join([header, "-"*len(header), print_student(s)])
