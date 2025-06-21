from typing import Any, List, Union, Tuple
from datetime import datetime
from orm.database import Cursor, DBFieldChanges
import orm.accounts
import orm.announcements
import orm.courseitems


class CourseGradingScheme:
    _value: int

    _DISABLED = 0
    _AVERAGE = 1
    _SUM = 2
    _MANUAL = 3
    _TEXT = ["disabled", "average", "sum", "manual"]

    def __init__(self, value: int):
        self._value = value

    @staticmethod
    def Disabled():
        return CourseGradingScheme(CourseGradingScheme._DISABLED)

    @staticmethod
    def Average():
        return CourseGradingScheme(CourseGradingScheme._AVERAGE)

    @staticmethod
    def Sum():
        return CourseGradingScheme(CourseGradingScheme._SUM)

    @staticmethod
    def Manual():
        return CourseGradingScheme(CourseGradingScheme._MANUAL)

    def __str__(self):
        return CourseGradingScheme._TEXT[self._value]

    def to_string(self):
        return str(self)

    def __eq__(self, other):
        return isinstance(other, CourseGradingScheme) and self._value == other._value

    @staticmethod
    def from_string(value: str) -> "CourseGradingScheme":
        return CourseGradingScheme(CourseGradingScheme._TEXT.index(value))


class CourseDTO:
    id: str
    timecreated: datetime
    name: str
    coursegradingscheme: CourseGradingScheme

    def __init__(self, id: str, timecreated: datetime, name: str, coursegradingscheme: CourseGradingScheme):
        self.id = id
        self.timecreated = timecreated
        self.name = name
        self.coursegradingscheme = coursegradingscheme


class Course:
    _cur: Cursor
    _id: str

    class CourseChanges(DBFieldChanges):
        def __init__(self):
            super().__init__()

        def change_name(self, new_value: str):
            return self.change_any_field("name", new_value)

        def change_course_grading_scheme(self, new_value: CourseGradingScheme):
            return self.change_any_field("coursegradingscheme", str(new_value))

        def course_compile_update(self, id: str):
            return self.compile_update("Course", "id = %s", (id,))

    def __init__(self, cur: Cursor, id: str):
        self._cur = cur
        self._id = id

    def exists(self) -> bool:
        return self._cur.exists("Course", id=self._id)

    def _request_fields(self, *args: str) -> tuple:
        return self._cur.request_fields_one_match("Course", "id = %s", (self._id,), *args)

    def _request_field(self, field: str) -> Any:
        return self._request_fields(field)[0]

    def get(self) -> CourseDTO:
        fields = list(self._request_fields("id", "timecreated", "name", "coursegradingscheme"))
        fields[-1] = CourseGradingScheme.from_string(fields[-1])
        return CourseDTO(*fields)

    def id(self) -> str:
        return self._id

    def time_created(self) -> datetime:
        return self._request_field("timecreated")

    def name(self) -> str:
        return self._request_field("name")

    def course_grading_scheme(self) -> CourseGradingScheme:
        return CourseGradingScheme.from_string(self._request_field("coursegradingscheme"))

    def set(self, changes: CourseChanges):
        self._cur.execute(*changes.course_compile_update(self._id))

    def create(self, name: str, course_grading_scheme: CourseGradingScheme):
        self._cur.execute("INSERT INTO Course VALUES (%s, now(), %s, %s)",
                          (self._id, name, str(course_grading_scheme)))

    def delete(self):
        self._cur.execute("DELETE FROM Course WHERE id = %s", (self._id,))

    def last_announcements(self, count: int, skip: int) -> List[orm.announcements.Announcement]:
        res = self._cur.request_fields_all_matches("CourseAnnouncement",
                                                   "courseid = %s ORDER BY timecreated DESC LIMIT %s OFFSET %s",
                                                   (self._id, count, skip), "annid")
        return [orm.announcements.Announcement(self._cur, self._id, row[0]) for row in res]

    def items(self) -> List[Union[orm.courseitems.MaterialCourseItem, orm.courseitems.GradeableCourseItem]]:
        rows = self._cur.request_fields_all_matches("CourseItem", "courseid = %s ORDER BY ordering, timecreated",
                                                    (self._id,), "itemid", "kind")
        res = []
        for itemid, kind_s in rows:
            kind = orm.courseitems.CourseItemKind.from_string(kind_s)
            if kind == orm.courseitems.CourseItemKind.Gradeable():
                res.append(orm.courseitems.GradeableCourseItem(self._cur, self._id, itemid))
            else:
                res.append(orm.courseitems.MaterialCourseItem(self._cur, self._id, itemid))
        return res

    def course_items(self) -> List[orm.courseitems.CourseItem]:
        rows = self._cur.request_fields_all_matches("CourseItem", "courseid = %s ORDER BY ordering, timecreated",
                                                    (self._id,), "itemid")
        return [orm.courseitems.CourseItem(self._cur, self._id, row[0]) for row in rows]

    def has_teacher(self, user: orm.accounts.Account) -> bool:
        return self._cur.exists("TeacherAt", teacherlogin=user.login(), courseid=self._id)

    def has_student(self, user: orm.accounts.Account) -> bool:
        return self._cur.exists("StudentAt", studentlogin=user.login(), courseid=self._id)

    def has_parent(self, user: orm.accounts.Account) -> bool:
        return self._cur.exists("ParentOfAt", parentlogin=user.login(), courseid=self._id)

    def all_students(self) -> List[orm.accounts.Account]:
        return [orm.accounts.Account(row[0]) for row in
                self._cur.request_fields_all_matches("StudentAt", "courseid = %s", (self._id,), "studentlogin")]

    def all_teachers(self) -> List[orm.accounts.Account]:
        return [orm.accounts.Account(row[0]) for row in
                self._cur.request_fields_all_matches("TeacherAt", "courseid = %s", (self._id,), "teacherlogin")]

    def all_parents(self) -> List[orm.accounts.Account]:
        return [orm.accounts.Account(row[0]) for row in
                self._cur.request_fields_all_matches("ParentOfAt", "courseid = %s", (self._id,),
                                                     "DISTINCT parentlogin")]

    def all_parents_of_students_pairs(self) -> List[Tuple[orm.accounts.Account, orm.accounts.Account]]:
        """
        Returns a list of pairs of accounts where the first account is the student and the second one is their parent.
        """
        return [tuple(map(orm.accounts.Account, row)) for row in
                self._cur.request_fields_all_matches("ParentOfAt", "courseid = %s", (self._id,),
                                                     "studentlogin", "parentlogin")]

    def all_parents_of_students(self, allow_no_parents: bool) -> \
            List[Tuple[orm.accounts.Account, List[orm.accounts.Account]]]:
        """
        Returns a list of pairs: (student, list of parents).
        If allow_no_parents is set, then all students are returned, some with empty lists of parents.
        If allow_no_parents is not set, then only students that have parents in this course are returned.
        """

        if allow_no_parents:
            rows = self._cur.request_fields_all_matches(
                "StudentAt s LEFT JOIN ParentOfAt p ON s.studentlogin = p.studentlogin",
                "s.courseid = %s ORDER BY studentlogin", (self._id,), "s.studentlogin", "p.parentlogin"
            )
        else:
            rows = self._cur.request_fields_all_matches("ParentOfAt", "courseid = %s ORDER BY studentlogin",
                                                        (self._id,), "studentlogin", "parentlogin")
        res = []
        for stud, par in rows:
            if par is None:
                res.append((orm.accounts.Account(self._cur, stud), []))
                continue
            par = orm.accounts.Account(self._cur, par)
            if res and res[-1][0].login() == stud:
                res[-1].append(par)
            else:
                res.append((orm.accounts.Account(self._cur, stud), [par]))
        return res

    def add_student(self, acc: orm.accounts.Account):
        self._cur.execute("INSERT INTO StudentAt VALUES (%s, %s)", (acc.login(), self._id))

    def add_teacher(self, acc: orm.accounts.Account):
        self._cur.execute("INSERT INTO TeacherAt VALUES (%s, %s)", (acc.login(), self._id))

    def add_parent(self, parent: orm.accounts.Account, student: orm.accounts.Account):
        self._cur.execute("INSERT INTO ParentOfAt VALUES (%s, %s, %s)", (parent.login(), student.login(), self._id))

    def remove_parent(self, parent: orm.accounts.Account):
        self._cur.delete("ParentOfAt", parentlogin=parent.login())

    def remove_parent_of_student(self, parent: orm.accounts.Account, student: orm.accounts.Account):
        self._cur.delete("ParentOfAt", parentlogin=parent.login(), studentlogin=student.login(), courseid=self._id)

    def remove_parents_of(self, student: orm.accounts.Account):
        self._cur.delete("ParentOfAt", studentlogin=student.login(), courseid=self._id)

    def remove_student(self, student: orm.accounts.Account):
        self._cur.delete("StudentAt", studentlogin=student.login(), courseid=self._id)

    def remove_teacher(self, teacher: orm.accounts.Teacher):
        self._cur.delete("TeacherAt", teacherlogin=teacher.login(), courseid=self._id)

    def teacher_count(self) -> int:
        return self._cur.request_field("TeacherAt", "courseid = %s", (self._id), "count(*)")
