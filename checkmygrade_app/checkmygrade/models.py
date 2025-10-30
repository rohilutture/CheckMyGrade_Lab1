from dataclasses import dataclass, asdict
from typing import Optional, List


def grade_from_marks(marks: int) -> str:
    if marks is None:
        return ""
    if marks >= 97:
        return "A+"
    if marks >= 93:
        return "A"
    if marks >= 90:
        return "A-"
    if marks >= 87:
        return "B+"
    if marks >= 83:
        return "B"
    if marks >= 80:
        return "B-"
    if marks >= 77:
        return "C+"
    if marks >= 73:
        return "C"
    if marks >= 70:
        return "C-"
    if marks >= 60:
        return "D"
    return "F"

@dataclass
class Student:
    email_address: str
    first_name: str
    last_name: str
    course_id: str
    grade: str
    marks: int

@dataclass
class Course:
    course_id: str
    course_name: str
    description: str = ""
    credits: int = 3

@dataclass
class Professor:
    professor_id: str  
    professor_name: str
    rank: str
    course_id: str

@dataclass
class LoginUser:
    user_id: str        
    password: str       
    role: str          

@dataclass
class GradeRange:
    grade_id: str
    grade: str
    min_marks: int
    max_marks: int
