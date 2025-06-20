from typing import Union, Any, List, Tuple
from repo.database import Cursor, DBFieldChanges
from datetime import datetime
import repo.courses


class AccountDTO:
    login: str
    passwordhash: bytes
    publicname: str
    timeregistered: datetime
    contactinfo: str
    avatar: Union[None, str]
    institutional: bool
    verified: bool

    def __init__(self, login: str, passwordhash: bytes, publicname: str, timeregistered: datetime, contactinfo: str,
                 avatar: Union[None, str], institutional: bool, verified: bool):
        self.login = login
        self.passwordhash = passwordhash
        self.publicname = publicname
        self.timeregistered = timeregistered
        self.contactinfo = contactinfo
        self.avatar = avatar
        self.institutional = institutional
        self.verified = verified


class Account:
    _cur: Cursor
    _login: str

    class AccountChanges(DBFieldChanges):
        def __init__(self):
            super().__init__()

        def change_password_hash(self, new_hash: bytes):
            return self.change_any_field("passwordhash", new_hash)

        def change_public_name(self, new_name: str):
            return self.change_any_field("publicname", new_name)

        def change_contactinfo(self, new_value: str):
            return self.change_any_field("contactinfo", new_value)

        def change_avatar(self, new_value: Union[None, str]):
            return self.change_any_field("avatar", new_value)

        def change_institutional(self, new_value: bool):
            return self.change_any_field("institutional", new_value)

        def change_verified(self, new_value: bool):
            return self.change_any_field("verified", new_value)

        def account_compile_update(self, login: str):
            return self.compile_update("Account", "login = %s", (login,))

    def __init__(self, cur: Cursor, login: str):
        self._cur = cur
        self._login = login

    def _request_fields(self, *args: str) -> tuple:
        return self._cur.request_fields_one_match("Account", "login = %s", (self._login,), *args)

    def _request_field(self, field: str) -> Any:
        return self._request_fields(field)[0]

    def exists(self) -> bool:
        return self._cur.exists("Account", login=self._login)

    def get(self) -> AccountDTO:
        return AccountDTO(*self._request_fields("login", "passwordhash", "publicname", "timeregistered", "contactinfo",
                                                "avatar", "institutional", "verified"))

    def login(self) -> str:
        return self._login

    def password_hash(self) -> bytes:
        return self._request_field("passwordhash").tobytes()

    def public_name(self) -> str:
        return self._request_field("publicname")

    def timeregistered(self) -> datetime:
        return self._request_field("timeregistered")

    def contactinfo(self) -> str:
        return self._request_field("contactinfo")

    def avatar(self) -> Union[None, str]:
        return self._request_field("avatar")

    def institutional(self) -> bool:
        return self._request_field("institutional")

    def verified(self) -> bool:
        return self._request_field("verified")

    def set(self, changes: AccountChanges):
        self._cur.execute(*changes.account_compile_update(self._login))

    def create(self, passwordhash: bytes, publicname: str, institutional: bool, verified: bool):
        self._cur.execute("INSERT INTO Account VALUES (%s, %s, %s, now(), '', null, %s, %s);",
                          (self._login, passwordhash, publicname, institutional, verified))

    def get_all_courses(self) -> List[repo.courses.Course]:
        self._cur.execute("""SELECT courseid FROM StudentAt WHERE studentlogin = %s
                          UNION SELECT courseid FROM TeacherAt WHERE teacherlogin = %s
                          UNION SELECT courseid FROM ParentOfAt WHERE parentlogin = %s""",
                          (self._login,) * 3)
        return [repo.courses.Course(self._cur, row[0]) for row in self._cur.fetchall()]

    def student_at_courses(self) -> List[repo.courses.Course]:
        return [repo.courses.Course(self._cur, row[0]) for row in
                self._cur.request_fields_all_matches("StudentAt", "studentlogin = %s", (self._login,), "courseid")]

    def teacher_at_courses(self) -> List[repo.courses.Course]:
        return [repo.courses.Course(self._cur, row[0]) for row in
                self._cur.request_fields_all_matches("TeacherAt", "studentlogin = %s", (self._login,), "courseid")]

    def parent_at_courses_of_students(self) -> "List[Tuple[repo.courses.Course, List[Account]]]":
        """
        Returns a list of all courses in which this user is a parent of some student(s).
        The children are returned alongside the course in which they are enrolled.
        """

        pairs = self._cur.request_fields_all_matches("ParentOfAt", "parentlogin = %s ORDER BY courseid", (self._login,),
                                                     "courseid", "studentlogin")
        res = []
        for cid, child in pairs:
            child_acc = Account(self._cur, child)
            if not res or res[-1][0].id() != cid:
                res.append((repo.courses.Course(self._cur, cid), [child_acc]))
            else:
                res[-1][1].append(child_acc)
        return res

    def parent_at_courses(self) -> List[repo.courses.Course]:
        """
        Returns a list of all courses in which this user is a parent of some student(s).
        The children are not returned.
        """
        res = self._cur.request_fields_all_matches("ParentOfAt", "parentlogin = %s", (self._login,), "DISTINCT courseid")
        return [repo.courses.Course(self._cur, row[0]) for row in res]

    def delete(self):
        self._cur.delete("Account", login=self._login)


"""
def sql_select_single_teacher_courses(db_cursor, user_email):
    db_cursor.execute(
        "SELECT t.courseid FROM teaches t WHERE t.email = %s AND (SELECT COUNT(*) FROM teaches WHERE courseid = t.courseid) = 1",
        (user_email,),
    )
    return [row[0] for row in db_cursor.fetchall()]
"""
