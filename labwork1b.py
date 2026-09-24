# Global data 

students = []   # each: {"id": str, "name": str, "dob": str}
courses = []    # each: {"id": str, "name": str}
marks = {}      # marks[course_id][student_id] = float


# Helper: read a positive integer safely

def read_positive_int(prompt):
    while True:
        raw = input(prompt).strip()
        if raw.isdigit() and int(raw) > 0:
            return int(raw)
        print("  Please enter a positive integer.")


# INPUT FUNCTIONS

def input_number_of_students():
    """Input number of students in a class."""
    return read_positive_int("Number of students in the class: ")


def input_student_information():
    """Input student information: id, name, DoB."""
    sid = input("  Student id: ").strip()
    name = input("  Student name: ").strip()
    dob = input("  Student DoB (dd/mm/yyyy): ").strip()
    return {"id": sid, "name": name, "dob": dob}


def input_number_of_courses():
    """Input number of courses."""
    return read_positive_int("Number of courses: ")


def input_course_information():
    """Input course information: id, name."""
    cid = input("  Course id: ").strip()
    name = input("  Course name: ").strip()
    return {"id": cid, "name": name}


def select_course():
    """Let the user pick a course by id. Returns the course dict or None."""
    if not courses:
        print("No courses available.")
        return None
    list_courses()
    cid = input("Select a course (enter course id): ").strip()
    for c in courses:
        if c["id"] == cid:
            return c
    print("Course not found.")
    return None


def input_marks_for_course():
    """Select a course, then input marks for every student in it."""
    if not students:
        print("No students available.")
        return
    course = select_course()
    if course is None:
        return

    marks.setdefault(course["id"], {})
    print(f"Entering marks for course: {course['name']}")
    for s in students:
        while True:
            raw = input(f"  Mark for {s['name']} ({s['id']}): ").strip()
            try:
                value = float(raw)
                if 0 <= value <= 20:          
                    marks[course["id"]][s["id"]] = value
                    break
                print("  Mark must be between 0 and 20.")
            except ValueError:
                print("  Please enter a number.")


# LISTING FUNCTIONS

def list_courses():
    """List courses."""
    if not courses:
        print("No courses yet.")
        return
    print("\n--- Courses ---")
    for c in courses:
        print(f"  {c['id']:<10} {c['name']}")


def list_students():
    """List students."""
    if not students:
        print("No students yet.")
        return
    print("\n--- Students ---")
    for s in students:
        print(f"  {s['id']:<10} {s['name']:<25} {s['dob']}")


def show_student_marks_for_course():
    """Show student marks for a given course."""
    course = select_course()
    if course is None:
        return
    course_marks = marks.get(course["id"], {})
    if not course_marks:
        print("No marks entered for this course yet.")
        return
    print(f"\n--- Marks for {course['name']} ---")
    for s in students:
        mark = course_marks.get(s["id"])
        shown = f"{mark:.1f}" if mark is not None else "N/A"
        print(f"  {s['id']:<10} {s['name']:<25} {shown}")



# MAIN

def setup_students():
    n = input_number_of_students()
    for i in range(n):
        print(f"Student {i + 1}/{n}")
        students.append(input_student_information())


def setup_courses():
    n = input_number_of_courses()
    for i in range(n):
        print(f"Course {i + 1}/{n}")
        courses.append(input_course_information())


def menu():
    print("""
===== Student Mark Management =====
1. Input students
2. Input courses
3. Input marks for a course
4. List courses
5. List students
6. Show student marks for a course
0. Exit""")


def main():
    actions = {
        "1": setup_students,
        "2": setup_courses,
        "3": input_marks_for_course,
        "4": list_courses,
        "5": list_students,
        "6": show_student_marks_for_course,
    }
    while True:
        menu()
        choice = input("Choose: ").strip()
        if choice == "0":
            print("Bye!")
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
