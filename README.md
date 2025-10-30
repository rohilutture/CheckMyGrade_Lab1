## CheckMyGrade — Lab 1 (DATA 200)

**Student:** Rohil Pravin Utture  
**Course:** DATA 200 — San José State University  
**Professor:** Paramdeep Saini  
**Date:** October 2025  

---

## Overview
**CheckMyGrade** is a console-based Python application that allows professors and students to manage grades efficiently.  
It demonstrates core **object-oriented programming** and **data structure** principles using arrays/lists and CSV file persistence.

The app supports:
- Adding, deleting, and updating **student**, **course**, and **professor** records  
- Searching (linear vs indexed) with **timing comparison**  
- Sorting by **marks, grade, name, or email**  
- **Course statistics** (average & median)  
- **Reports** (course-wise, professor-wise, student-wise)  
- **Password encryption/decryption** for secure login  
- Persistent storage via CSV files  

---

## Data Structures Used
- **Python lists** (`students`, `courses`, `professors`, `login_users`) – dynamic arrays used to store records.  
- **Dictionary index** for quick lookup of students by email — improves search speed over linear scanning.

---

## Key Features
| Feature | Description |
|----------|-------------|
| CRUD | Add/Delete/Update students, courses, professors |
| Sorting | Sort by marks, grade, or name (timed) |
| Searching | Linear vs Indexed search (timed) |
| Statistics | Average and median by course |
| Reports | Course-wise, Professor-wise, and Student-wise |
| CSV | Data persistence with read/write operations |
| Encryption | XOR + random IV + Base64 reversible cipher for passwords |
| Tests | 1100-record dataset tested using Python’s `unittest` |

---

## Unit Test Summary
All **6 test modules** executed successfully:
- Student CRUD  
- Course/Professor CRUD  
- Search (linear vs indexed) with timing output  
- Sorting performance  
- Statistics and reports  
- Encryption/decryption integrity  

Run tests:
```bash
set PYTHONPATH=.
python -m unittest discover -s tests -v
