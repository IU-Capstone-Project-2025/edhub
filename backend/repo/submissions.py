from typing import Union, Any, Tuple, override
from datetime import datetime
from repo.database import Cursor, DBFieldChanges


class AssignmentSubmissionDTO:
    courseid: str
    itemid: str
    submittedby: str
    timecreated: datetime
    timemodified: datetime
    comment: str

    def __init__(self, courseid: str, itemid: str, submittedby: str,
                 timecreated: datetime, timemodified: datetime, comment: str):
        self.courseid = courseid
        self.itemid = itemid
        self.submittedby = submittedby
        self.timecreated = timecreated
        self.timemodified = timemodified
        self.comment = comment


class AssignmentSubmission:
    _cur: Cursor
    _courseid: str
    _itemid: str
    _submittedby: str

    _PRIMARY_KEY_SQL = "courseid = %s AND itemid = %s AND submittedby = %s"

    def _primary_key(self) -> Tuple[str, str, str]:
        return (self._courseid, self._itemid, self._submittedby)

    class AssignmentSubmissionChanges(DBFieldChanges):
        def __init__(self):
            super().__init__()
            self.add_custom_update("timemodified = now()")

        def change_comment(self, new_value: str):
            return self.change_any_field("comment", new_value)

        def assignment_submission_compile_update(self, courseid: str, itemid: str, submittedby: str):
            return self.compile_update("AssignmentSubmission", AssignmentSubmission._PRIMARY_KEY_SQL,
                                       (courseid, itemid, submittedby))

        @override
        def copy(self) -> "AssignmentSubmission.AssignmentSubmissionChanges":
            res = AssignmentSubmission.AssignmentSubmissionChanges()
            res.copy_from(self)
            return res

    def __init__(self, cursor: Cursor, course_id: str, item_id: str, submitted_by: str):
        self._cur = cursor
        self._courseid = course_id
        self._itemid = item_id
        self._submittedby = submitted_by

    def request_fields(self, *fields: str) -> tuple:
        return self._cur.request_fields_one_match("AssignmentSubmission", AssignmentSubmission._PRIMARY_KEY_SQL,
                                                  self._where_args(), *fields)

    def request_field(self, field: str) -> Any:
        return self.request_fields(field)[0]

    def exists(self) -> bool:
        return self._cur.exists_custom("AssignmentSubmission", AssignmentSubmission._PRIMARY_KEY_SQL, self._where_args())

    def get(self) -> AssignmentSubmissionDTO:
        return AssignmentSubmissionDTO(*self.request_fields("courseid", "itemid", "submittedby",
                                                            "timecreated", "timemodified", "comment"))

    def courseid(self) -> str:
        return self._courseid

    def itemid(self) -> str:
        return self._itemid

    def submittedby(self) -> str:
        return self._submittedby

    def timecreated(self) -> datetime:
        return self.request_field("timecreated")

    def timemodified(self) -> datetime:
        return self.request_field("timemodified")

    def comment(self) -> str:
        return self.request_field("comment")

    def set(self, changes: AssignmentSubmissionChanges):
        self._cur.execute(*changes.assignment_submission_compile_update(*self._primary_key()))

    def create(self, comment: str):
        self._cur.execute("INSERT INTO AssignmentSubmission VALUES (%s, %s, %s, now(), now(), %s)",
                          (self._courseid, self._itemid, self._submittedby, comment))

    def grade(self) -> "CourseItemGrade":
        return CourseItemGrade(self._cur, *self._primary_key())

    def graded(self) -> bool:
        return self.grade().exists()

    def touch(self):
        """
        Sets timemodified to the current time. Happens automatically, do not call it after every set().
        """
        self.set(AssignmentSubmission.AssignmentSubmissionChanges())


class CourseItemGradeDTO:
    courseid: str
    itemid: str
    studentlogin: str
    grade: int
    gradedby: Union[None, str]
    timecreated: datetime
    comment: str

    def __init__(self, courseid: str, itemid: str, studentlogin: str, grade: int, gradedby: Union[None, str],
                 timecreated: datetime, comment: str):
        self.courseid = courseid
        self.itemid = itemid
        self.studentlogin = studentlogin
        self.grade = grade
        self.gradedby = gradedby
        self.timecreated = timecreated
        self.comment = comment


class CourseItemGrade:
    _cur: Cursor
    _courseid: str
    _itemid: str
    _studentlogin: str

    _PRIMARY_KEY_SQL = "courseid = %s AND itemid = %s AND studentlogin = %s"

    class CourseItemGradeChanges(DBFieldChanges):
        def __init__(self):
            super().__init__()

        def change_grade(self, new_value: int) -> "CourseItemGrade.CourseItemGradeChanges":
            return self.change_any_field("grade", new_value)

        def change_gradedby(self, new_value: Union[None, str]) -> "CourseItemGrade.CourseItemGradeChanges":
            return self.change_any_field("gradedby", new_value)

        def change_timecreated(self, new_value: datetime) -> "CourseItemGrade.CourseItemGradeChanges":
            return self.change_any_field("timecreated", new_value)

        def change_comment(self, new_value: str) -> "CourseItemGrade.CourseItemGradeChanges":
            return self.change_any_field("comment", new_value)

        def course_item_grade_compile_update(self, courseid: str, itemid: str, studentlogin: str) -> Tuple[str, tuple]:
            return self.compile_update("CourseItemGrade", CourseItemGrade._PRIMARY_KEY_SQL, (courseid, itemid, studentlogin))

    def _primary_key(self) -> Tuple[str, str, str]:
        return (self._courseid, self._itemid, self._studentlogin)

    def __init__(self, cursor: Cursor, course_id: str, item_id: str, student_login: str):
        self._cur = cursor
        self._courseid = course_id
        self._itemid = item_id
        self._studentlogin = student_login

    def request_fields(self, *fields: str) -> tuple:
        return self._cur.request_fields_one_match("CourseItemGrade", CourseItemGrade._PRIMARY_KEY_SQL,
                                                  self._primary_key(), *fields)

    def request_field(self, field: str) -> Any:
        return self.request_fields(field)[0]

    def exists(self) -> bool:
        return self._cur.exists_custom("CourseItemGrade", CourseItemGrade._PRIMARY_KEY_SQL, self._primary_key())

    def get(self) -> CourseItemGradeDTO:
        return CourseItemGradeDTO(*self.request_fields("courseid", "itemid", "studentlogin", "grade",
                                                       "gradedby", "timecreated", "comment"))

    def courseid(self) -> str:
        return self._courseid

    def itemid(self) -> str:
        return self._itemid

    def studentlogin(self) -> str:
        return self._studentlogin

    def grade(self) -> int:
        return self.request_field("grade")

    def above_max(self) -> bool:
        self._cur.execute("""SELECT i.maxgrade IS NOT NULL AND i.maxgrade < g.grade FROM CourseItemGrade g
                          JOIN GradeableCourseItem i ON g.courseid = i.courseid AND g.itemid = i.itemid
                          WHERE g.courseid = %s AND g.itemid = %s AND g.studentlogin = %s""", self._primary_key())
        return self._cur.fetchone()[0]

    def gradedby(self) -> Union[None, str]:
        return self.request_field("gradedby")

    def timecreated(self) -> datetime:
        return self.request_field("timecreated")

    def comment(self) -> str:
        return self.request_field("comment")

    def grade_is_stale(self) -> bool:
        """
        Returns true if the grading happened earlier than the last submission.
        """

        self._cur.execute("""SELECT s.timemodified > g.timecreated FROM CourseItemGrade g
                          JOIN AssignmentSubmission s
                          ON s.courseid = g.courseid AND s.itemid = g.itemid AND s.submittedby = g.studentlogin
                          WHERE g.courseid = %s AND g.itemid = %s AND g.studentlogin = %s""", self._primary_key())
        return self._cur.fetchone()[0]

    def set(self, changes: CourseItemGradeChanges):
        self._cur.execute(*changes.course_item_grade_compile_update(*self._primary_key()))

    def delete(self):
        self._cur.delete_custom("CourseItemGrade", CourseItemGrade._PRIMARY_KEY_SQL, self._primary_key())

    def create(self, grade: int, gradedby: str, comment: str):
        self._cur.execute("INSERT INTO CourseItemGrade VALUES (%s, %s, %s, %s, %s, now(), %s)",
                          (self._courseid, self._itemid, self._studentlogin, grade, gradedby, comment))
