CREATE DATABASE edhub;
\c edhub

CREATE TABLE users(
    email text PRIMARY KEY CHECK (length(email) <= 254),
    publicname text NOT NULL,
    isadmin bool NOT NULL,
    timeregistered timestamp NOT NULL,
    passwordhash text NOT NULL
);

CREATE TABLE courses(
    courseid uuid PRIMARY KEY,
    name text NOT NULL CHECK (length(name) <= 128),
    timecreated timestamp NOT NULL
);

CREATE TABLE course_materials(
    courseid uuid REFERENCES courses ON DELETE CASCADE,
    matid serial NOT NULL, -- problem: only 2'000'000'000 courses per deployed database; proposed: change to uuid
    timeadded timestamp NOT NULL,
    author text NULL REFERENCES users(email) ON DELETE SET NULL,
    name text NOT NULL CHECK (length(name) <= 100),
    description text NOT NULL CHECK (length(description) <= 1000),
    PRIMARY KEY (courseid, matid)
);

CREATE TABLE course_assignments(
    courseid uuid REFERENCES courses ON DELETE CASCADE,
    assid serial NOT NULL, -- problem: only 2'000'000'000 courses per deployed database; proposed: change to uuid 
    timeadded timestamp NOT NULL,
    author text NULL REFERENCES users(email) ON DELETE SET NULL,
    name text NOT NULL CHECK (length(name) <= 100),
    description text NOT NULL CHECK (length(description) <= 1000),
    PRIMARY KEY (courseid, assid)
);

CREATE TABLE course_assignments_submissions(
    courseid uuid REFERENCES courses ON DELETE CASCADE,
    assid int REFERENCES course_assignments ON DELETE CASCADE,
    email text REFERENCES users ON DELETE CASCADE,
    timeadded timestamp NOT NULL,
    timemodified timestamp NOT NULL,
    comment text NOT NULL CHECK (length(comment) <= 1000),
    grade int NOT NULL,
    gradedby text NULL REFERENCES users ON DELETE SET NULL,
    PRIMARY KEY (courseid, assid, email)
);

CREATE TABLE teaches(
    email text REFERENCES users ON DELETE CASCADE,
    courseid uuid REFERENCES courses ON DELETE CASCADE,
    PRIMARY KEY (email, courseid)
);

CREATE TABLE student_at(
    email text REFERENCES users ON DELETE CASCADE,
    courseid uuid REFERENCES courses ON DELETE CASCADE,
    PRIMARY KEY (email, courseid)
);

CREATE TABLE parent_of_at_course(
    parentemail text REFERENCES users ON DELETE CASCADE,
    studentemail text REFERENCES users ON DELETE CASCADE,
    courseid uuid REFERENCES courses ON DELETE CASCADE,
    FOREIGN KEY (studentemail, courseid) REFERENCES student_at ON DELETE CASCADE,
    PRIMARY KEY (parentemail, studentemail, courseid)
);

