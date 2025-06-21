from fastapi.responses import JSONResponse


USER_NOT_FOUND = "USER_NOT_FOUND"
USER_EXISTS = "USER_EXISTS"
COURSE_NOT_FOUND = "COURSE_NOT_FOUND"
PARAMETER_NOT_INTEGER = "NOT_INTEGER"
COURSE_ITEM_NOT_FOUND = "COURSE_ITEM_NOT_FOUND"
NO_ACCESS_TO_COURSE = "NO_ACCESS_TO_COURSE"
USER_LACKS_ROLE_IN_COURSE = "USER_LACKS_ROLE_IN_COURSE"
NOT_AN_ASSIGNMENT = "NOT_AN_ASSIGNMENT"
NO_SUBMISSION_TO_ASSIGNMENT = "NO_SUBMISSION_TO_ASSIGNMENT"


class EdHubException(Exception):
    _code: int
    _detail: str
    _exc_name: str
    _kwargs: object

    def __init__(self, code: int, detail: str, exc_name: str, **kwargs: object):
        super().__init__(code)
        self._code = code
        self._detail = detail
        self._exc_name = exc_name
        self._kwargs = kwargs

    def json_response(self) -> JSONResponse:
        return JSONResponse(status_code=self._code,
                            content={"detail": self._detail, "exc_name": self._exc_name, "args": self._kwargs})


class AccountNotFoundException(EdHubException):
    def __init__(self, user_login: str):
        super().__init__(404, f"The following user login is not registered in the system: {user_login}",
                         USER_NOT_FOUND, user_login)


class UserExistsException(EdHubException):
    def __init__(self, user_login: str):
        super().__init__(403, f"The following user login has already been registered in the system: {user_login}",
                         USER_EXISTS, user_login)


class CourseNotFoundException(EdHubException):
    def __init__(self, course_id: str):
        super().__init__(404, f"The course ID {course_id} does not match any course", COURSE_NOT_FOUND, course_id)


class ParameterNotIntegerException(EdHubException):
    def __init__(self, param_name: str, value: str):
        super().__init__(400, f"The value of parameter \"{param_name}\" must be integer, but received \"{value}\"",
                         PARAMETER_NOT_INTEGER, param_name, value)


class CourseItemNotFoundException(EdHubException):
    def __init__(self, course_id: str, item_id: int):
        super().__init__(404, f"In the course {course_id}, the item {item_id} does not exist",
                         COURSE_ITEM_NOT_FOUND, course_id, item_id)


class NoAccessToCourseException(EdHubException):
    def __init__(self, course_id: str, user_login: str):
        super().__init__(403, f"The user \"{user_login}\" has no access to the course {course_id}",
                         NO_ACCESS_TO_COURSE, course_id, user_login)


class UserLacksRoleInCourseException(EdHubException):
    def __init__(self, course_id: str, user_login: str, role: str):
        super().__init__(403, f"The user \"{user_login}\" must have the \"{role}\" role in the course {course_id}, but does not",
                         USER_LACKS_ROLE_IN_COURSE, course_id, user_login, role)


class NotAnAssignmentException(EdHubException):
    def __init__(self, course_id: str, item_id: int):
        super().__init__(403, f"In the course {course_id}, the item {item_id} is not an assignment",
                         NOT_AN_ASSIGNMENT, course_id, item_id)


class NoSubmissionToAssignment(EdHubException):
    def __init__(self, course_id: str, assignment_item_id: int, user_login: str):
        super().__init__(404, f"In the course {course_id}, the user \"{user_login}\" has not submitted anything for the assignment {assignment_item_id}",
                         NO_SUBMISSION_TO_ASSIGNMENT, course_id, assignment_item_id, user_login)
