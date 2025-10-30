import sys, os
from pathlib import Path
from .storage import CheckMyGradeDB
from .models import Student, Course, Professor
from .reports import render_course_report, render_professor_report, render_student_report

def seed_sample(db: CheckMyGradeDB):
    # only if empty
    if not db.courses:
        db.add_course(Course("DATA200","Data Science","Intro to DS & Python",3))
        db.add_course(Course("MATH101","Calculus I","Differential calculus",4))
    if not db.professors:
        db.add_professor(Professor("micheal@mycsu.edu", "Micheal John", "Senior Professor", "DATA200"))
        db.add_professor(Professor("alice@mycsu.edu", "Alice Smith", "Assistant Professor", "MATH101"))
    if not db.students:
        db.add_student(Student("sam@mycsu.edu", "Sam", "Carpenter", "DATA200", "A", 96))
        db.add_student(Student("jane@mycsu.edu", "Jane", "Lopez", "DATA200", "", 88))
        db.add_student(Student("bob@mycsu.edu", "Bob", "Nguyen", "MATH101", "", 73))
    if not db.login_users:
        db.register_user("micheal@mycsu.edu", "Welcome12#_", role="professor")

def print_menu():
    print("""
===== CheckMyGrade =====
1) List students
2) Add student
3) Update student
4) Delete student
5) Search student (linear vs indexed)
6) Sort students (email/marks/name/grade)
7) Course stats (avg, median)
8) Reports (course/professor/student)
9) Save to CSV
10) Load from CSV
11) Login test
0) Exit
""")

def main():
    data_dir = os.environ.get("CMG_DATA_DIR", str(Path.cwd() / "data"))
    db = CheckMyGradeDB(data_dir)
    # load or seed
    if Path(data_dir).exists():
        db.load_all()
    seed_sample(db)
    while True:
        print_menu()
        choice = input("Choose: ").strip()
        if choice == "1":
            for s in db.students:
                print(f"{s.email_address:25s} | {s.first_name:10s} {s.last_name:12s} | {s.course_id:8s} | {s.grade:3s} | {s.marks:3d}")
        elif choice == "2":
            email = input("Email: ").strip()
            fn = input("First name: ").strip()
            ln = input("Last name: ").strip()
            cid = input("Course id: ").strip()
            marks = int(input("Marks (0-100): ").strip())
            db.add_student(Student(email,fn,ln,cid,"",marks))
            print("Added.")
        elif choice == "3":
            email = input("Student email to update: ").strip()
            field = input("Field (first_name,last_name,course_id,marks): ").strip()
            value = input("New value: ").strip()
            if field == "marks":
                value = int(value)
            ok = db.update_student(email, **{field: value})
            print("Updated." if ok else "Student not found.")
        elif choice == "4":
            email = input("Student email to delete: ").strip()
            ok = db.delete_student(email)
            print("Deleted." if ok else "Student not found.")
        elif choice == "5":
            email = input("Student email to search: ").strip()
            s1, t1 = db.search_student_linear(email)
            s2, t2 = db.search_student_indexed(email)
            print(f"Linear search: {('FOUND' if s1 else 'not found')} in {t1*1000:.3f} ms")
            print(f"Indexed search: {('FOUND' if s2 else 'not found')} in {t2*1000:.3f} ms")
        elif choice == "6":
            by = input("Sort by (email/marks/name/grade): ").strip()
            asc = input("Ascending? (y/n): ").strip().lower() != "n"
            t = db.sort_students(by=by, ascending=asc)
            print(f"Sorted in {t*1000:.3f} ms")
        elif choice == "7":
            cid = input("Course id: ").strip()
            stats = db.course_stats(cid)
            print(stats)
        elif choice == "8":
            which = input("Report (course/professor/student): ").strip().lower()
            if which == "course":
                cid = input("Course id: ").strip()
                print(render_course_report(db, cid))
            elif which == "professor":
                pid = input("Professor id (email): ").strip()
                print(render_professor_report(db, pid))
            else:
                email = input("Student email: ").strip()
                print(render_student_report(db, email))
        elif choice == "9":
            db.save_all(); print("Saved.")
        elif choice == "10":
            db.load_all(); print("Loaded.")
        elif choice == "11":
            email = input("Email: ").strip()
            pw = input("Password: ").strip()
            ok = db.login(email, pw)
            print("Login OK" if ok else "Login failed")
        elif choice == "0":
            print("Bye")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
