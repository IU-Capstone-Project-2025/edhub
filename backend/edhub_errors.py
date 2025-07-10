from fastapi.responses import JSONResponse

INVALID_TOKEN_STRUCTURE = "INVALID_TOKEN_STRUCTURE"
TOKEN_EXPIRED = "TOKEN_EXPIRED"
JWT_ERROR = "JWT_ERROR"
USER_NOT_FOUND = "USER_NOT_FOUND"
USER_EXISTS = "USER_EXISTS"
COURSE_NOT_FOUND = "COURSE_NOT_FOUND"
NOT_INTEGER = "NOT_INTEGER"
MATERIAL_NOT_FOUND = "MATERIAL_NOT_FOUND"
ASSIGNMENT_NOT_FOUND = "ASSIGNMENT_NOT_FOUND"
NO_ACCESS_TO_COURSE = "NO_ACCESS_TO_COURSE"
USER_LACKS_ROLE_IN_COURSE = "USER_LACKS_ROLE_IN_COURSE"
USER_HAS_DIFFERENT_ROLE_IN_COURSE = "USER_HAS_DIFFERENT_ROLE_IN_COURSE"
NOT_PARENT_OF_STUDENT = "NOT_PARENT_OF_STUDENT"
ALREADY_PARENT_OF_STUDENT = "ALREADY_PARENT_OF_STUDENT"
NO_SUBMISSION_TO_ASSIGNMENT = "NO_SUBMISSION_TO_ASSIGNMENT"
NOT_AN_ADMIN = "NOT_AN_ADMIN"
CANNOT_REMOVE_PARENT = "CANNOT_REMOVE_PARENT"
FILE_TOO_LARGE = "FILE_TOO_LARGE"


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


class InvalidTokenStructureException(EdHubException):
    def __init__(self):
        super().__init__(401, "Invalid token structure", INVALID_TOKEN_STRUCTURE)


class TokenExpiredException(EdHubException):
    def __init__(self):
        super().__init__(401, "Token expired", TOKEN_EXPIRED)


class CustomJWTException(EdHubException):
    def __init__(self, message: str):
        super().__init__(401, message, JWT_ERROR, internal_message=message)


class UserNotFoundException(EdHubException):
    def __init__(self, user_login: str):
        super().__init__(404, f"This user login is not registered in the system: {user_login}",
                         USER_NOT_FOUND, user_login=user_login)


class UserExistsException(EdHubException):
    def __init__(self, user_login: str):
        super().__init__(403, f"This user login has already been registered in the system: {user_login}",
                         USER_EXISTS, user_login=user_login)


class CourseNotFoundException(EdHubException):
    def __init__(self, course_id: str):
        super().__init__(404, f"The course ID {course_id} does not match any course",
                         COURSE_NOT_FOUND, course_id=course_id)


class MaterialNotFoundException(EdHubException):
    def __init__(self, course_id: str, material_id: int):
        super().__init__(404, f"The course {course_id} does not contain material {material_id}",
                         MATERIAL_NOT_FOUND, course_id=course_id, material_id=material_id)


class AssignmentNotFoundException(EdHubException):
    def __init__(self, course_id: str, assignment_id: int):
        super().__init__(404, f"The course {course_id} does not contain assignment {assignment_id}",
                         ASSIGNMENT_NOT_FOUND, course_id=course_id, assignment_id=assignment_id)


class ParameterNotIntegerException(EdHubException):
    def __init__(self, param_name: str, value: str):
        super().__init__(400, f"The value of parameter \"{param_name}\" must be integer, but received \"{value}\"",
                         NOT_INTEGER, param_name=param_name, value=value)


class NoAccessToCourseException(EdHubException):
    def __init__(self, course_id: str, user_login: str):
        super().__init__(403, f"The user \"{user_login}\" has no access to the course {course_id}",
                         NO_ACCESS_TO_COURSE, course_id=course_id, user_login=user_login)


class UserLacksRoleInCourseException(EdHubException):
    def __init__(self, course_id: str, user_login: str, role: str):
        super().__init__(403, f"The user \"{user_login}\" must have the \"{role}\" role in the course {course_id}, but does not",
                         USER_LACKS_ROLE_IN_COURSE, course_id=course_id, user_login=user_login, role=role)


class UserIsNotTeacherInCourseException(UserLacksRoleInCourseException):
    def __init__(self, course_id: str, user_login: str):
        super().__init__(course_id, user_login, "teacher")


class UserIsNotParentInCourseException(UserLacksRoleInCourseException):
    def __init__(self, course_id: str, user_login: str):
        super().__init__(course_id, user_login, "parent")


class UserIsNotParentOfStudentInCourseException(EdHubException):
    def __init__(self, course_id: str, user_login: str, student_login: str):
        super().__init__(403, f"In course {course_id}, the user \"{user_login}\" is not a parent of \"{student_login}\"",
                         NOT_PARENT_OF_STUDENT, course_id=course_id, user_login=user_login, student_login=student_login)


class UserIsAlreadyParentOfStudentInCourseException(EdHubException):
    def __init__(self, course_id: str, user_login: str, student_login: str):
        super().__init__(403, f"In course {course_id}, the user \"{user_login}\" is already a parent of \"{student_login}\"",
                         ALREADY_PARENT_OF_STUDENT, course_id=course_id, user_login=user_login, student_login=student_login)


class UserIsNotStudentInCourseException(UserLacksRoleInCourseException):
    def __init__(self, course_id: str, user_login: str):
        super().__init__(course_id, user_login, "student")


class UserAlreadyHasDifferentRoleException(EdHubException):
    def __init__(self, course_id: str, user_login: str, oldrole: str, newrole: str):
        super.__init__(403, f"In course {course_id}, the user \"{user_login}\" already has the role \"{oldrole}\", cannot assign role \"{newrole}\"",
                       USER_HAS_DIFFERENT_ROLE_IN_COURSE, course_id=course_id, oldrole=oldrole, newrole=newrole)


class NoSubmissionToAssignmentException(EdHubException):
    def __init__(self, course_id: str, assignment_id: int, user_login: str):
        super().__init__(404, f"In the course {course_id}, the user \"{user_login}\" has not submitted anything for the assignment {assignment_id}",
                         NO_SUBMISSION_TO_ASSIGNMENT, course_id=course_id, assignment_id=assignment_id, user_login=user_login)


class NotAnAdminException(EdHubException):
    def __init__(self, user_login: str):
        super().__init__(403, f"The user \"{user_login}\" is not an admin", NOT_AN_ADMIN, user_login=user_login)


class CannotRemoveParentException(EdHubException):
    def __init__(self, course_id: str, user_login: str, parent_login: str):
        super().__init__(403, f"The user \"{user_login}\" must be admin, the teacher at course {course_id}, or \"{parent_login}\" to revoke the parent access of \"{parent_login}\"",
                         CANNOT_REMOVE_PARENT, course_id=course_id, user_login=user_login, parent_login=parent_login)


class FileTooLargeException(EdHubException):
    def __init__(self, max_size: int):
        super().__init__(413, f"The file you tried to upload was too large (max {max_size} bytes)",
                         FILE_TOO_LARGE, max_size=max_size)
