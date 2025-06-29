CREATE DATABASE edhub;
\c edhub
CREATE TABLE users(
    email text PRIMARY KEY CHECK (length(email) <= 254),
    publicname text NOT NULL CHECK (length(publicname) <= 128),
    isadmin bool NOT NULL DEFAULT 'f',
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
    matid serial NOT NULL,
    timeadded timestamp NOT NULL,
    author text NULL REFERENCES users(email) ON DELETE SET NULL,
    name text NOT NULL CHECK (length(name) <= 100),
    description text NOT NULL CHECK (length(description) <= 1000),
    PRIMARY KEY (courseid, matid)
);

CREATE TABLE course_assignments(
    courseid uuid REFERENCES courses ON DELETE CASCADE,
    assid serial NOT NULL,
    timeadded timestamp NOT NULL,
    author text NULL REFERENCES users(email) ON DELETE SET NULL,
    name text NOT NULL CHECK (length(name) <= 100),
    description text NOT NULL CHECK (length(description) <= 1000),
    PRIMARY KEY (courseid, assid)
);

CREATE TABLE course_assignments_submissions(
    courseid uuid REFERENCES courses ON DELETE CASCADE,
    assid int,
    email text REFERENCES users ON DELETE CASCADE,
    timeadded timestamp NOT NULL,
    timemodified timestamp NOT NULL CHECK (timemodified >= timeadded),
    comment text NOT NULL CHECK (length(comment) <= 1000),
    grade int NOT NULL,
    gradedby text NULL REFERENCES users ON DELETE SET NULL,
    FOREIGN KEY (courseid, assid) REFERENCES course_assignments ON DELETE CASCADE,
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

CREATE TABLE logs(
    t timestamp NOT NULL,
    tag text NOT NULL,
    msg text NOT NULL
);

create table material_files(
    courseid uuid,
    matid int,
    fileid serial,
    filename text NOT NULL,
    file bytea NOT NULL,
    upload_time timestamp NOT NULL,
    FOREIGN KEY (courseid, matid) REFERENCES course_materials ON DELETE CASCADE,
    PRIMARY KEY (courseid, matid, fileid)
);

create table assignment_files(
    courseid uuid,
    assid int,
    fileid serial,
    filename text NOT NULL,
    file bytea NOT NULL,
    upload_time timestamp NOT NULL,
    FOREIGN KEY (courseid, assid) REFERENCES course_assignments ON DELETE CASCADE,
    PRIMARY KEY (courseid, assid, fileid)
);

create table submissions_files(
    courseid uuid,
    assid int,
    email text,
    fileid serial,
    filename text NOT NULL,
    file bytea NOT NULL,
    upload_time timestamp NOT NULL,
    FOREIGN KEY (courseid, assid, email) REFERENCES course_assignments_submissions ON DELETE CASCADE,
    PRIMARY KEY (courseid, assid, email, fileid)
);
