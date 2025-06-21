from typing import Tuple, Any, List, Union
from datetime import datetime
from repo.database import Cursor, DBFieldChanges


class CourseItemKind:
    _MATERIAL = 0
    _GRADEABLE = 1
    _TEXT = ["material", "gradeable"]

    _value: int

    def __init__(self, value: int):
        self._value = value

    def __str__(self) -> str:
        return CourseItemKind._TEXT[self._value]

    def __eq__(self, other) -> bool:
        return isinstance(other, CourseItemKind) and other._value == self._value

    def to_string(self) -> str:
        return str(self)

    @staticmethod
    def from_string(value: str) -> "CourseItemKind":
        return CourseItemKind(CourseItemKind._TEXT.index(value))

    @staticmethod
    def Material():
        return CourseItemKind(CourseItemKind._MATERIAL)

    @staticmethod
    def Gradeable():
        return CourseItemKind(CourseItemKind._GRADEABLE)


class CourseItemDTO:
    courseid: str
    itemid: str
    ordering: int
    timecreated: datetime
    title: str
    kind: CourseItemKind
    comment: str

    def __init__(self, courseid: str, itemid: str, ordering: int, timecreated: datetime,
                 title: str, kind: CourseItemKind, comment: str):
        self.courseid = courseid
        self.itemid = itemid
        self.ordering = ordering
        self.timecreated = timecreated
        self.title = title
        self.kind = kind
        self.comment = comment


class CourseItemGradeCriterionDTO:
    courseid: str
    itemid: str
    points: int
    comment: str

    def __init__(self, courseid: str, itemid: str, points: int, comment: str):
        self.courseid = courseid
        self.itemid = itemid
        self.points = points
        self.comment = comment


class GradeableCourseItemDTO:
    maxpoints: Union[None, int]
    assignment: bool
    courseitem: CourseItemDTO

    def __init__(self, courseitem: CourseItemDTO, maxpoints: Union[None, int], assignment: bool):
        self.courseitem = courseitem
        self.maxpoints = maxpoints
        self.assignment = assignment


class CourseItem:
    _cur: Cursor
    _courseid: str
    _itemid: str

    class CourseItemChanges(DBFieldChanges):
        def __init__(self):
            super().__init__()

        def change_ordering(self, new_value: int):
            return self.change_any_field("ordering", new_value)

        def change_title(self, new_value: str):
            return self.change_any_field("title", new_value)

        def change_comment(self, new_value: str):
            return self.change_any_field("comment", new_value)

        def course_item_compile_update(self, courseid: str, itemid: str) -> Tuple[str, tuple]:
            return self.compile_update("CourseItem", "courseid = %s AND itemid = %s", (courseid, itemid))

    def __init__(self, cur: Cursor, courseid: str, itemid: str):
        self._cur = cur
        self._courseid = courseid
        self._itemid = itemid

    def exists(self) -> bool:
        return self._cur.exists("CourseItem", courseid=self._courseid, itemid=self._itemid)

    def request_fields(self, *fields: str) -> tuple:
        return self._cur.request_fields_one_match("CourseItem", "courseid = %s AND itemid = %s",
                                                  (self._courseid, self._itemid))

    def request_field(self, field: str) -> Any:
        return self.request_fields(field)[0]

    def get(self) -> list:
        values = list(self.request_fields("courseid", "itemid", "ordering", "timecreated", "title", "kind", "comment"))
        values[5] = CourseItemKind.from_string(values[5])
        return CourseItemDTO(*values)

    def courseid(self) -> str:
        return self._courseid

    def itemid(self) -> str:
        return self._itemid

    def ordering(self) -> int:
        return self.request_field("ordering")

    def timecreated(self) -> datetime:
        return self.request_field("timecreated")

    def title(self) -> str:
        return self.request_field("title")

    def kind(self) -> CourseItemKind:
        return CourseItemKind.from_string(self.request_field("kind"))

    def comment(self) -> str:
        return self.request_field("comment")

    def set(self, changes: CourseItemChanges):
        self._cur.execute(*changes.course_item_compile_update(self._courseid, self._itemid))

    def delete(self):
        self._cur.delete("CourseItem", courseid=self._courseid, itemid=self._itemid)

    @staticmethod
    def create(cursor: Cursor, courseid: str, title: str, comment: str, kind: CourseItemKind) -> "CourseItem":
        cursor.execute("""WITH maxorder AS (SELECT max(ordering) as order FROM CourseItem WHERE courseid = %s)
                       INSERT INTO CourseItem SELECT %s, gen_random_uuid(), maxorder.order + 1, now(), %s, %s, %s
                       FROM maxorder RETURNING itemid""",
                       (courseid, courseid, title, str(kind), comment))
        itemid = cursor.fetchone()[0]
        return CourseItem(cursor, courseid, itemid)


class CourseItemGradeCriterion:
    _cur: Cursor
    _courseid: str
    _itemid: str
    _points: int

    _PRIMARY_KEY_SQL = "courseid = %s AND itemid = %s AND points = %s"

    def __init__(self, cursor: Cursor, course_id: str, item_id: str, points: int):
        self._cur = cursor
        self._courseid = course_id
        self._itemid = item_id
        self._points = points

    def request_fields(self, *fields: str) -> tuple:
        return self._cur.request_fields_one_match("CourseItemGradeCriterion", CourseItemGradeCriterion._PRIMARY_KEY_SQL,
                                                  (self._courseid, self._itemid, self._points), *fields)

    def request_field(self, field: str) -> Any:
        return self.request_fields(field)[0]

    def get(self) -> CourseItemGradeCriterionDTO:
        return CourseItemGradeCriterionDTO(*self.request_fields("courseid", "itemid", "points", "comment"))

    def courseid(self) -> str:
        return self.request_field("courseid")

    def itemid(self) -> str:
        return self.request_field("itemid")

    def points(self) -> int:
        return self.request_field("points")

    def comment(self) -> str:
        return self.request_field("comment")

    def set_comment(self, new_comment: str):
        self._cur.execute(f"UPDATE CourseItemGradeCriterion SET comment = %s WHERE {CourseItemGradeCriterion._PRIMARY_KEY_SQL}",
                          (new_comment, self._courseid, self._itemid, self._points))


class GradeableCourseItem:
    _cur: Cursor
    _courseid: str
    _itemid: str

    class GradeableCourseItemChanges(DBFieldChanges):
        def __init__(self):
            super().__init__()

        def change_maxpoints(self, new_value: Union[None, int]):
            return self.change_any_field("maxpoints", new_value)

        def change_is_assignment(self, new_value: bool):
            return self.change_any_field("assignment", new_value)

        def gradeable_course_item_compile_update(self, courseid: str, itemid: str) -> Tuple[str, tuple]:
            return self.compile_update("GradeableCourseItem", "courseid = %s AND itemid = %s", (courseid, itemid))

    def __init__(self, cursor: Cursor, course_id: str, item_id: str):
        self._cur = cursor
        self._courseid = course_id
        self._itemid = item_id

    def exists(self) -> bool:
        return self._cur.exists("GradeableCourseItem", courseid=self._courseid, itemid=self._itemid)

    def course_item(self) -> CourseItem:
        return CourseItem(self._cur, self._courseid, self._itemid)

    def request_fields(self, *fields: str) -> tuple:
        return self._cur.request_fields_one_match("GradeableCourseItem", "courseid = %s AND itemid = %s",
                                                  (self._courseid, self._itemid), *fields)

    def request_field(self, field: str) -> Any:
        return self.request_fields(field)[0]

    def get(self) -> GradeableCourseItemDTO:
        return GradeableCourseItemDTO(self._course_item.get(), *self.request_fields("maxpoints", "assignment"))

    def maxpoints(self) -> Union[None, int]:
        return self.request_field("maxpoints")

    def assignment(self) -> bool:
        return self.request_field("assignment")

    def set(self, changes: GradeableCourseItemChanges):
        self._cur.execute(*changes.gradeable_course_item_compile_update(self._courseid, self._itemid))

    def delete(self):
        self.course_item().delete()

    def criteria(self) -> List[CourseItemGradeCriterion]:
        rows = self._cur.request_fields_all_matches("CourseItemGradeCriterion", "courseid = %s AND itemid = %s",
                                                    (self._courseid, self._itemid), "points")
        return [CourseItemGradeCriterion(self._cur, self._courseid, self._itemid, row[0]) for row in rows]

    def add_criteria(self, criteria: List[Tuple[int, str]]):
        if not criteria:
            return
        values = []
        for points, comment in criteria:
            values.extend([self._courseid, self._itemid, points, comment])
        self._cur.execute(f"INSERT INTO CourseItemGradeCriterion VALUES {", ".join(("(%s, %s, %s, %s)",) * len(criteria))}",
                          tuple(values))

    def clear_criteria(self):
        self._cur.delete("CourseItemGradeCriterion", courseid=self._courseid, itemid=self._itemid)

    def set_criteria(self, criteria: List[Tuple[int, str]]):
        self.clear_criteria()
        self.add_criteria(criteria)

    @staticmethod
    def create(cursor: Cursor, courseid: str, title: str, comment: str,
               maxpoints: Union[None, int], assignment: bool) -> "GradeableCourseItem":
        courseitem = CourseItem.create(cursor, courseid, title, comment, CourseItemKind.Gradeable())
        itemid = courseitem.itemid()
        cursor.execute("INSERT INTO GradeableCourseItem VALUES (%s, %s, %s, %s)",
                       (courseid, itemid, maxpoints, assignment))
        return GradeableCourseItem(cursor, courseid, itemid)


class MaterialCourseItem:
    _cur: Cursor
    _courseid: str
    _itemid: str

    def __init__(self, cursor: Cursor, course_id: str, item_id: str):
        self._cur = cursor
        self._courseid = course_id
        self._itemid = item_id

    def course_item(self) -> CourseItem:
        return CourseItem(self._cur, self._courseid, self._itemid)

    def delete(self):
        self.course_item().delete()

    @staticmethod
    def create(cursor: Cursor, course_id: str, title: str, comment: str):
        courseitem = CourseItem.create(cursor, course_id, title, comment, CourseItemKind.Material())
        return MaterialCourseItem(cursor, course_id, courseitem.itemid())
