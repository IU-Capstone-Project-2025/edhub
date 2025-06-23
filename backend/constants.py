from os import path

# time format for the creation time
TIME_FORMAT = "%m-%d-%Y %H:%M:%S"

# directories to store the files
UPLOAD_BASE_DIR = "/app/uploads"
ASSIGNMENTS_DIR = path.join(UPLOAD_BASE_DIR, "assignments")
SUBMISSIONS_DIR = path.join(UPLOAD_BASE_DIR, "submissions")
MATERIALS_DIR = path.join(UPLOAD_BASE_DIR, "materials")

# maximum size of the attached file
MAX_FILE_SIZE = 5 * 1024 * 1024