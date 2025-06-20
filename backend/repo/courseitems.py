from datetime import datetime
from repo.database import Database, DBFieldChanges


class CourseItemKind:
    _MATERIAL = 0
    _ASSIGNMENT = 1
    _CUSTOM_GRADE = 2
    _TEXT = ["material", "assignment", "customgrade"]

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
    def Material():
        return CourseItemKind(CourseItemKind._MATERIAL)

    @staticmethod
    def Assignment():
        return CourseItemKind(CourseItemKind._ASSIGNMENT)

    @staticmethod
    def CustomGrade():
        return CourseItemKind(CourseItemKind._CUSTOM_GRADE)


class CourseItemDTO:
    courseid: str
    itemid: int
    ordering: int
    timecreated: datetime
    title: str
    kind: CourseItemKind
    comment: str

    def __init__(self, courseid: str, itemid: int, ordering: int, timecreated: datetime,
                 title: str, kind: CourseItemKind, comment: str):
        self.courseid = courseid
        self.itemid = itemid
        self.ordering = ordering
        self.timecreated = timecreated
        self.title = title
        self.kind = kind
        self.comment = comment


class CourseItem:
    _cur: Cursor
    _courseid: str
    _itemid: int


