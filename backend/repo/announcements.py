from typing import Any, Union
from datetime import datetime
from database import Cursor
import repo.courses


class AnnouncementDTO:
    courseid: str
    annid: str
    author: Union[None, str]
    timecreated: datetime
    title: str
    content: str

    def __init__(self, courseid: str, annid: str, author: Union[None, str],
                 timecreated: datetime, title: str, content: str):
        self.courseid = courseid
        self.annid = annid
        self.author = author
        self.timecreated = timecreated
        self.title = title
        self.content = content


class Announcement:
    _cur: Cursor
    _courseid: str
    _annid: int

    def __init__(self, cur: Cursor, course_id: str, announcement_id: int):
        self._cur = cur
        self._courseid = course_id
        self._annid = announcement_id

    def exists(self) -> bool:
        return self._cur.exists("CourseAnnouncement", courseid=self._courseid, annid=self._annid)

    def _request_fields(self, *fields: str) -> tuple:
        return self._cur.request_fields_one_match("CourseAnnouncement", "courseid = %s AND annid = %s",
                                                  (self._courseid, self._annid), *fields)

    def _request_field(self, field: str) -> Any:
        return self._request_fields(field)[0]

    def get(self) -> AnnouncementDTO:
        return AnnouncementDTO(*self._request_fields("courseid", "annid", "author", "timecreated", "title", "content"))

    def course(self) -> repo.courses.Course:
        return repo.courses.Course(self._cur, self._courseid)

    def announcement_id(self) -> str:
        return self._annid

    def author(self) -> Union[None, repo.accounts.Account]:
        login = self._requeset_field("author")
        if login is None:
            return None
        return repo.courses.Account(self._cur, login)

    def time_created(self) -> datetime:
        return self._request_field("timecreated")

    def title(self) -> str:
        return self._request_field("title")

    def content(self) -> str:
        return self._request_field("content")

    @staticmethod
    def create(cursor: Cursor, course_id: str, author_login: str, title: str, content: str) -> "Announcement":
        cursor.execute("""INSERT INTO CourseAnnouncement VALUES (%s, gen_random_uuid(), %s, now(), %s, %s)
                       RETURNING annid""", course_id, author_login, title, content)
        annid = cursor.fetchone()[0]
        return Announcement(cursor, course_id, annid)

    def delete(self):
        self._cur.delete("CourseAnnouncement", courseid=self._courseid, annid=self._annid)
