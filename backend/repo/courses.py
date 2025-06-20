from typing import Any, List
from datetime import datetime
from repo.database import Cursor, DBFieldChanges
import repo.accounts
import repo.announcements
import repo.courseitems


class CourseGradingScheme:
    _value: int

    _AVERAGE = 0
    _SUM = 1
    _TEXT = ["average", "sum"]

    def __init__(self, value: int):
        self._value = value

    @staticmethod
    def Average():
        return CourseGradingScheme(CourseGradingScheme._AVERAGE)

    @staticmethod
    def Sum():
        return CourseGradingScheme(CourseGradingScheme._SUM)

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
    nextannid: int
    nextitemid: int
    totalgradeenabled: bool
    coursegradingscheme: CourseGradingScheme

    def __init__(self, id: str, timecreated: datetime, name: str, nextannid: int, nextitemid: int,
                 totalgradeenabled: bool, coursegradingscheme: CourseGradingScheme):
        self.id = id
        self.timecreated = timecreated
        self.name = name
        self.nextannid = nextannid
        self.nextitemid = nextitemid
        self.totalgradeenabled = totalgradeenabled
        self.coursegradingscheme = coursegradingscheme


class Course:
    _cur: Cursor
    _id: str

    class CourseChanges(DBFieldChanges):
        def __init__(self):
            super().__init__()

        def change_name(self, new_value: str):
            return self.change_any_field("name", new_value)

        def change_total_grade_enabled(self, new_value: bool):
            return self.change_any_field("totalgradeenabled", new_value)

        def change_course_grading_scheme(self, new_value: CourseGradingScheme):
            return self.change_any_field("coursegradingscheme", new_value)

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
        fields = list(self._request_fields("id", "timecreated", "name", "nextannid", "nextitemid",
                                           "totalgradeenabled", "coursegradingscheme"))
        fields[-1] = CourseGradingScheme.from_string(fields[-1])
        return CourseDTO(*fields)

    def id(self) -> str:
        return self._id

    def time_created(self) -> datetime:
        return self._request_field("timecreated")

    def name(self) -> str:
        return self._request_field("name")

    def nextannid(self) -> int:
        return self._request_field("nextannid")

    def nextitemid(self) -> int:
        return self._request_field("nextitemid")

    def total_grade_enabled(self) -> bool:
        return self._request_field("totalgradeenabled")

    def course_grading_scheme(self) -> CourseGradingScheme:
        return CourseGradingScheme(self._request_field("coursegradingscheme"))

    def set(self, changes: CourseChanges):
        self._cur.execute(*changes.course_compile_update(self._id))

    def create(self, name: str, total_grade_enabled: bool, course_grading_scheme: CourseGradingScheme):
        self._cur.execute("""INSERT INTO Course(id, timecreated, name, totalgradeenabled, coursegradingscheme)
                          VALUES (%s, now(), %s, %s, %s)""", (self._id, name, total_grade_enabled,
                                                              str(course_grading_scheme)))

    def delete(self):
        self._cur.execute("DELETE FROM Course WHERE id = %s", (self._id,))

    def last_announcements(self, count: int, skip: int) -> List[repo.announcements.Announcement]:
        res = self._cur.request_fields_all_matches("CourseAnnouncement",
                                                   "courseid = %s ORDER BY timecreated LIMIT %s OFFSET %s",
                                                   (self._id, count, skip), "annid")
        return [repo.announcements.Announcement(self._cur, self._id, row[0]) for row in res]

    def items(self) -> List[repo.courseitems.CourseItem]:
        res = self._cur.request_fields_all_matches("CourseItem", "courseid = %s ORDER BY ordering, timecreated",
                                                   (self._id,), "itemid")
        return [repo.courseitems.CourseItem(self._cur, self._id, row[0]) for row in res]


def sql_select_course_feed(db_cursor, course_id):
    db_cursor.execute(
        """
        SELECT courseid AS cid, matid as postid, 'mat' as type, timeadded, author
        FROM course_materials
        WHERE courseid = %s

        UNION

        SELECT courseid AS cid, assid as postid, 'ass' as type, timeadded, author
        FROM course_assignments
        WHERE courseid = %s

        ORDER BY timeadded DESC
        """,
        (course_id, course_id),
    )
    return db_cursor.fetchall()
