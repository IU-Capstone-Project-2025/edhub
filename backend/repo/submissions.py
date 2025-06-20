from typing import Union, Any, List, Tuple, override
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

    _AFTER_WHERE = "courseid = %s AND itemid = %s AND submittedby = %s"

    def _primary_key(self) -> Tuple[str, str, str]:
        return (self._courseid, self._itemid, self._submittedby)

    class AssignmentSubmissionChanges(DBFieldChanges):
        def __init__(self):
            super().__init__()

        def change_comment(self, new_value: str):
            return self.change_any_field("comment", new_value)

        def assignment_submission_compile_update(self, courseid: str, itemid: str, submittedby: str):
            return self.compile_update("AssignmentSubmission", AssignmentSubmission._AFTER_WHERE,
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
        return self._cur.request_fields_one_match("AssignmentSubmission", AssignmentSubmission._AFTER_WHERE,
                                                  self._where_args(), *fields)

    def request_field(self, field: str) -> Any:
        return self.request_fields(field)[0]

    def exists(self) -> bool:
        return self._cur.exists_custom("AssignmentSubmission", AssignmentSubmission._AFTER_WHERE, self._where_args())

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
        changes = changes.copy()
        changes.add_custom_update("timemodified = now()")
        self._cur.execute(*changes.assignment_submission_compile_update(self._courseid, self._itemid, self._submittedby))

    def create(self, comment: str):
        self._cur.execute("INSERT INTO AssignmentSubmission VALUES (%s, %s, %s, now(), now(), %s)",
                          (self._courseid, self._itemid, self._submittedby, comment))

    def graded(self) -> bool:
        return AssignmentGrade(self._cur, *self._primary_key()).exists()


class AssignmentGradeDTO:
    courseid: str
    itemid: str
    submittedby: str
    grade: int
    gradedby: Union[None, str]
    timecreated: datetime
    comment: Union[None, str]

    def __init__(self, courseid: str, itemid: str, submittedby: str, grade: int, gradedby: Union[None, str],
                 timecreated: datetime, comment: Union[None, str]):
        self.courseid = courseid
        self.itemid = itemid
        self.submittedby = submittedby
        self.grade = grade
        self.gradedby = gradedby
        self.timecreated = timecreated
        self.comment = comment


class AssignmentGrade:
    _cur: Cursor
    _courseid: str
    _itemid: str
    _submittedby: str

    _AFTER_WHERE = "courseid = %s AND itemid = %s AND submittedby = %s"

    def _primary_key(self) -> Tuple[str, str, str]:
        return (self._courseid, self._itemid, self._submittedby)

    def __init__(self, cursor: Cursor, course_id: str, item_id: str, submitted_by: str):
        self._cur = cursor
        self._courseid = course_id
        self._itemid = item_id
        self._submittedby = submitted_by

    def request_fields(self, *fields: str) -> tuple:
        return self._cur.request_fields_one_match("AssignmentGrade", AssignmentGrade._AFTER_WHERE,
                                                  self._primary_key(), *fields)

    def request_field(self, field: str) -> Any:
        return self.request_fields(field)[0]

    def exists(self) -> bool:
        return self._cur.exists_custom("AssignmentGrade", AssignmentGrade._AFTER_WHERE, self._primary_key())

    def get(self) -> AssignmentGradeDTO:
        return AssignmentGradeDTO(*self.request_fields("courseid", "itemid", "submittedby", "grade",
                                                       "gradedby", "timecreated", "comment"))

    def courseid(self) -> str:
        return self._courseid

    def itemid(self) -> str:
        return self._itemid

    def submittedby(self) -> str:
        return self._submittedby

    def grade(self) -> int:
        return self.request_field("grade")

    def gradedby(self) -> Union[None, str]:
        return self.request_field("gradedby")

    def timecreated(self) -> datetime:
        return self.request_field("timecreated")

    def comment(self) -> Union[None, str]:
        return self.request_field("comment")

    def grade_is_stale(self) -> bool:
        """
        Returns true if the grading happened earlier than the last submission.
        """

        self._cur.execute("""SELECT s.timemodified > g.timecreated FROM AssignmentGrade g
                          JOIN AssignmentSubmission s
                          ON s.courseid = g.courseid AND s.itemid = g.itemid AND s.submittedby = g.submittedby
                          WHERE g.courseid = %s AND g.itemid = %s AND g.submittedby = %s""", self._primary_key())
        return self._cur.fetchone()[0]

    def set(self, 
