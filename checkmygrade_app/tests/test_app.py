import unittest, tempfile, random, string
from pathlib import Path
from checkmygrade.storage import CheckMyGradeDB
from checkmygrade.models import Student, Course, Professor, grade_from_marks
from checkmygrade.security import encrypt_password, decrypt_password

class CheckMyGradeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = CheckMyGradeDB(self.tmp.name)
        self.db.add_course(Course("DATA200","Data Science","Intro DS",3))
        self.db.add_course(Course("CS146","Data Structures","DS & Algos",3))
        self.db.add_professor(Professor("micheal@mycsu.edu","Micheal John","Senior Professor","DATA200"))
        self.db.add_professor(Professor("dev@mycsu.edu","Dev Patel","Associate Professor","CS146"))
        random.seed(7)
        first_names = ["Sam","Alex","Jamie","Taylor","Riley","Jordan","Cameron"]
        last_names = ["Kim","Lopez","Nguyen","Carpenter","Singh","Patel","Park"]
        for i in range(1100):
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            email = f"{fn.lower()}{i}@sjsu.edu"
            course_id = "DATA200" if i % 2 == 0 else "CS146"
            marks = random.randint(40, 100)
            self.db.add_student(Student(email, fn, ln, course_id, "", marks))
        self.db.save_all()
        self.db.load_all()

    def tearDown(self):
        self.tmp.cleanup()

    def test_student_crud(self):
        email = "newstudent@sjsu.edu"
        self.assertFalse(self.db._student_index.get(email))
        self.db.add_student(Student(email,"New","Student","DATA200","",81))
        self.assertTrue(self.db._student_index.get(email) is not None)
        self.assertTrue(self.db.update_student(email, marks=95))
        s,_ = self.db.search_student_indexed(email)
        self.assertEqual(s.grade, grade_from_marks(95))
        self.assertTrue(self.db.delete_student(email))
        s,_ = self.db.search_student_indexed(email)
        self.assertIsNone(s)

    def test_search_timing(self):
        target = self.db.students[0].email_address
        s1, t1 = self.db.search_student_linear(target)
        s2, t2 = self.db.search_student_indexed(target)
        print("\n--- Timing: Search (linear vs indexed) ---")
        print(f"Target: {target}")
        print(f"Linear: {t1*1000:.3f} ms")
        print(f"Indexed: {t2*1000:.3f} ms")
        self.assertIsNotNone(s1)
        self.assertIsNotNone(s2)
        self.assertGreaterEqual(t1, 0.0)
        self.assertGreaterEqual(t2, 0.0)


    def test_sorting(self):
        t_email = self.db.sort_students(by="email", ascending=True)
        t_marks = self.db.sort_students(by="marks", ascending=False)
        self.assertGreaterEqual(t_email, 0.0)
        self.assertGreaterEqual(t_marks, 0.0)
        marks = [s.marks for s in self.db.students]
        self.assertTrue(all(marks[i] >= marks[i+1] for i in range(len(marks)-1)))

    def test_course_professor_crud(self):
        self.assertTrue(self.db.update_course("DATA200", description="Updated desc"))
        self.assertTrue(self.db.update_professor("micheal@mycsu.edu", rank="Distinguished Professor"))
        self.assertTrue(self.db.delete_course("CS146"))
        self.assertTrue(self.db.delete_professor("dev@mycsu.edu"))

    def test_stats_and_reports(self):
        stats = self.db.course_stats("DATA200")
        self.assertGreater(stats["count"], 0)
        students_for_prof = self.db.report_professor_wise("micheal@mycsu.edu")
        self.assertTrue(all(s.course_id == "DATA200" for s in students_for_prof))

    def test_encryption(self):
        token = encrypt_password("Welcome12#_")
        plain = decrypt_password(token)
        self.assertEqual(plain, "Welcome12#_")

if __name__ == "__main__":
    unittest.main()
