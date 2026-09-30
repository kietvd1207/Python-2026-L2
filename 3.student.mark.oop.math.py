import curses
import math

import numpy as np

MAX_MARK = 20


def floor_1dp(x):
    return math.floor(round(x * 10, 6)) / 10


class Course:
    def __init__(self, cid, name, credits):
        self.id = cid
        self.name = name
        self.credits = credits

    def __str__(self):
        return f"{self.id:<10} {self.name:<25} {self.credits} credit(s)"


class Student:
    def __init__(self, sid, name, dob):
        self.id = sid
        self.name = name
        self.dob = dob
        self.marks = {}

    def set_mark(self, course_id, mark):
        self.marks[course_id] = mark

    def gpa(self, courses):
        ids = [cid for cid in self.marks if cid in courses]
        if not ids:
            return None
        credits = np.array([courses[cid].credits for cid in ids], dtype=float)
        scores = np.array([self.marks[cid] for cid in ids], dtype=float)
        return float(np.dot(credits, scores) / credits.sum())

    def __str__(self):
        return f"{self.id:<10} {self.name:<25} {self.dob}"


class School:

    def __init__(self):
        self.students = []
        self.courses = {}


    def find_student(self, sid):
        return next((s for s in self.students if s.id == sid), None)


    def add_student(self, student):
        self.students.append(student)

    def add_course(self, course):
        self.courses[course.id] = course


    def all_gpas(self):
        return np.array(
            [np.nan if (g := s.gpa(self.courses)) is None else g
             for s in self.students],
            dtype=float,
        )

    def sort_students_by_gpa(self):
        gpas = np.nan_to_num(self.all_gpas(), nan=-1.0)
        order = np.argsort(-gpas, kind="stable")
        self.students = [self.students[i] for i in order]


class UI:
    TITLE, OK, ERR, SEL, DIM = 1, 2, 3, 4, 5

    def __init__(self, stdscr):
        self.scr = stdscr
        self.row = 0
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(self.TITLE, curses.COLOR_CYAN, -1)
        curses.init_pair(self.OK, curses.COLOR_GREEN, -1)
        curses.init_pair(self.ERR, curses.COLOR_RED, -1)
        curses.init_pair(self.SEL, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(self.DIM, curses.COLOR_YELLOW, -1)

    def begin(self, title):
        self.scr.erase()
        h, w = self.scr.getmaxyx()
        bar = "=" * (w - 1)
        self.say(bar, self.TITLE)
        self.say(f"  {title}", self.TITLE, curses.A_BOLD)
        self.say(bar, self.TITLE)
        self.row = 4

    def say(self, text, color=0, extra=0):
        h, w = self.scr.getmaxyx()
        if self.row >= h - 1:
            return
        attr = (curses.color_pair(color) if color else 0) | extra
        self.scr.addstr(self.row, 0, text[: w - 1], attr)
        self.row += 1

    def ask(self, prompt):
        h, w = self.scr.getmaxyx()
        row = min(self.row, h - 2)
        self.scr.addstr(row, 2, prompt[: w - 5])
        self.scr.refresh()
        curses.echo()
        curses.curs_set(1)
        raw = self.scr.getstr(row, min(2 + len(prompt), w - 2), 60)
        curses.noecho()
        curses.curs_set(0)
        self.row = row + 1
        return raw.decode(errors="ignore").strip()

    def ask_int(self, prompt):
        while True:
            raw = self.ask(prompt)
            if raw.isdigit() and int(raw) > 0:
                return int(raw)
            self.say("  Please enter a positive integer.", self.ERR)

    def pause(self, msg="Press any key to continue..."):
        h, _ = self.scr.getmaxyx()
        self.scr.addstr(h - 1, 0, msg, curses.color_pair(self.DIM))
        self.scr.refresh()
        self.scr.getch()

    def menu(self, title, options):
        idx = 0
        while True:
            self.begin(title)
            for i, text in enumerate(options):
                if i == idx:
                    self.say(f"  > {text:<40}", self.SEL, curses.A_BOLD)
                else:
                    self.say(f"    {text}")
            self.row += 1
            self.say("  Up/Down: move   Enter: select", self.DIM)
            self.scr.refresh()
            key = self.scr.getch()
            if key in (curses.KEY_UP, ord("k")):
                idx = (idx - 1) % len(options)
            elif key in (curses.KEY_DOWN, ord("j")):
                idx = (idx + 1) % len(options)
            elif key in (curses.KEY_ENTER, 10, 13):
                return idx


class App:
    def __init__(self, ui):
        self.ui = ui
        self.school = School()


    def input_students(self):
        ui = self.ui
        ui.begin("Input students")
        n = ui.ask_int("Number of students in the class: ")
        for i in range(n):
            ui.begin(f"Student {i + 1}/{n}")
            while True:
                sid = ui.ask("Student id: ")
                if not sid:
                    ui.say("  Id cannot be empty.", ui.ERR)
                elif self.school.find_student(sid):
                    ui.say("  This id already exists.", ui.ERR)
                else:
                    break
            name = ui.ask("Student name: ")
            dob = ui.ask("Student DoB (dd/mm/yyyy): ")
            self.school.add_student(Student(sid, name, dob))
        ui.say(f"Added {n} student(s).", ui.OK)
        ui.pause()

    def input_courses(self):
        ui = self.ui
        ui.begin("Input courses")
        n = ui.ask_int("Number of courses: ")
        for i in range(n):
            ui.begin(f"Course {i + 1}/{n}")
            while True:
                cid = ui.ask("Course id: ")
                if not cid:
                    ui.say("  Id cannot be empty.", ui.ERR)
                elif cid in self.school.courses:
                    ui.say("  This id already exists.", ui.ERR)
                else:
                    break
            name = ui.ask("Course name: ")
            credits = ui.ask_int("Course credits: ")
            self.school.add_course(Course(cid, name, credits))
        ui.say(f"Added {n} course(s).", ui.OK)
        ui.pause()

    def select_course(self, title):
        ui = self.ui
        ui.begin(title)
        if not self.school.courses:
            ui.say("No courses available.", ui.ERR)
            ui.pause()
            return None
        for c in self.school.courses.values():
            ui.say(f"  {c}")
        ui.row += 1
        cid = ui.ask("Select a course (enter course id): ")
        course = self.school.courses.get(cid)
        if course is None:
            ui.say("Course not found.", ui.ERR)
            ui.pause()
        return course

    def input_marks(self):
        ui = self.ui
        if not self.school.students:
            ui.begin("Input marks")
            ui.say("No students available.", ui.ERR)
            ui.pause()
            return
        course = self.select_course("Input marks - choose a course")
        if course is None:
            return
        ui.begin(f"Marks for {course.name} (0-{MAX_MARK}, floored to 1 decimal)")
        for s in self.school.students:
            while True:
                raw = ui.ask(f"Mark for {s.name} ({s.id}): ")
                try:
                    value = float(raw)
                except ValueError:
                    ui.say("  Please enter a number.", ui.ERR)
                    continue
                if 0 <= value <= MAX_MARK:
                    stored = floor_1dp(value)
                    s.set_mark(course.id, stored)
                    ui.say(f"  saved: {stored:.1f}", ui.OK)
                    break
                ui.say(f"  Mark must be between 0 and {MAX_MARK}.", ui.ERR)
        ui.pause()


    def list_courses(self):
        ui = self.ui
        ui.begin("Courses")
        if not self.school.courses:
            ui.say("No courses yet.", ui.ERR)
        for c in self.school.courses.values():
            ui.say(f"  {c}")
        ui.pause()

    def list_students(self):
        ui = self.ui
        ui.begin("Students")
        if not self.school.students:
            ui.say("No students yet.", ui.ERR)
        for s in self.school.students:
            ui.say(f"  {s}")
        ui.pause()

    def show_marks(self):
        ui = self.ui
        course = self.select_course("Show marks - choose a course")
        if course is None:
            return
        ui.begin(f"Marks for {course.name}")
        for s in self.school.students:
            mark = s.marks.get(course.id)
            shown = f"{mark:.1f}" if mark is not None else "N/A"
            ui.say(f"  {s.id:<10} {s.name:<25} {shown}")
        ui.pause()


    def show_gpa(self):
        ui = self.ui
        ui.begin("Average GPA of a student")
        if not self.school.students:
            ui.say("No students available.", ui.ERR)
            ui.pause()
            return
        sid = ui.ask("Student id: ")
        s = self.school.find_student(sid)
        if s is None:
            ui.say("Student not found.", ui.ERR)
        else:
            g = s.gpa(self.school.courses)
            if g is None:
                ui.say(f"{s.name} has no marks yet.", ui.ERR)
            else:
                ui.say(f"  {s.name}: GPA = {g:.2f} / {MAX_MARK}", ui.OK)
        ui.pause()

    def sort_and_show(self):
        ui = self.ui
        self.school.sort_students_by_gpa()
        ui.begin("Students sorted by GPA (descending)")
        if not self.school.students:
            ui.say("No students yet.", ui.ERR)
        else:
            ui.say(f"  {'Rank':<6}{'ID':<10} {'Name':<25} GPA", ui.DIM)
            for rank, s in enumerate(self.school.students, 1):
                g = s.gpa(self.school.courses)
                shown = f"{g:.2f}" if g is not None else "N/A"
                ui.say(f"  {rank:<6}{s.id:<10} {s.name:<25} {shown}")
        ui.pause()


    def run(self):
        options = [
            "Input students",
            "Input courses",
            "Input marks for a course",
            "List courses",
            "List students",
            "Show student marks for a course",
            "Show average GPA of a student",
            "Sort students by GPA (descending)",
            "Exit",
        ]
        actions = [
            self.input_students,
            self.input_courses,
            self.input_marks,
            self.list_courses,
            self.list_students,
            self.show_marks,
            self.show_gpa,
            self.sort_and_show,
        ]
        while True:
            choice = self.ui.menu("Student Mark Management", options)
            if choice == len(options) - 1:
                break
            actions[choice]()


def main(stdscr):
    App(UI(stdscr)).run()


if __name__ == "__main__":
    curses.wrapper(main)
    print("Bye!")
