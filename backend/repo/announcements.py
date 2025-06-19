from typing import Any
from datetime import datetime
from repo.database import Database
import repo.courses


class AnnouncementDTO:
    courseid: str
    annid: str
    timecreated: datetime
    title: str
    content: str

    def __init__(self, courseid: str, annid: str, timecreated: datetime, title: str, content: str):
        self.courseid = courseid
        self.annid = annid
        self.timecreated = timecreated
        self.title = title
        self.content = content


class Announcement:
    _db: Database
    _courseid: str
    _annid: int

    def __init__(self, db: Database, course_id: str, announcement_id: int):
        self._db = db
        self._courseid = course_id
        self._annid = announcement_id

    def exists(self) -> bool:
        with self._db.get_connection() as (conn, cur):
            cur.execute("SELECT EXISTS(SELECT 1 FROM CourseAnnouncement WHERE courseid = %s AND annid = %s",
                        (self._courseid, self._annid))
            return cur.fetchone()[0]

    def _request_fields(self, *fields: str) -> tuple:
        return self._db.request_fields_one_match("CourseAnnouncement", "courseid = %s AND annid = %s",
                                                 (self._courseid, self._annid), *fields)

    def _request_field(self, field: str) -> Any:
        return self._request_fields(field)[0]

    def get(self) -> AnnouncementDTO:
        return AnnouncementDTO(*self._request_fields("courseid", "annid", "timecreated", "title", "content"))

    def course(self) -> repo.courses.Course:
        return repo.courses.Course(self._db, self._courseid)

    def announcement_id(self) -> str:
        return self._annid

    def time_created(self) -> datetime:
        return self._request_field("timecreated")

    def title(self) -> str:
        return self._request_field("title")

    def content(self) -> str:
        return self._request_field("content")

    def create(self, title: str, content: str):
        with self._db.get_connection() as (conn, cur):
            cur.execute("""WITH aid AS (UPDATE Course SET lastannid = lastannid + 1 WHERE id = %s RETURNING lastannid)
                        INSERT INTO CourseAnnouncement SELECT %s, aid.lastannid, now(), %s, %s FROM aid""",
                        (self._courseid, self._courseid, title, content))
            conn.commit()

    def delete(self):
        with self._db.get_connection() as (conn, cur):
            cur.execute("DELETE FROM CourseAnnouncement WHERE courseid = %s, annid = %s", (self._courseid, self._annid))
