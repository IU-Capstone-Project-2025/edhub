CREATE DATABASE edhub;
\c edhub
<<<<<<< logging
create table users(email text primary key, publicname text, isadmin bool, timeregistered timestamp, passwordhash text);
create table courses(courseid uuid primary key, name text, timecreated timestamp);
create table course_materials(courseid uuid references courses on delete cascade, matid serial, timeadded timestamp, author text references users(email) on delete set null,
    name text, description text, primary key (courseid, matid));
create table course_assignments(courseid uuid references courses on delete cascade, assid serial, timeadded timestamp, author text references users(email) on delete set null,
    name text, description text, primary key (courseid, assid));
create table course_assignments_submissions(courseid uuid references courses on delete cascade, assid int references course_assignments on delete cascade,
    email text references users on delete cascade, timeadded timestamp, timemodified timestamp, comment text, grade int, gradedby text references users on delete set null,
    primary key (courseid, assid, email));
create table teaches(email text references users on delete cascade, courseid uuid references courses on delete cascade,
    primary key (email, courseid));
create table student_at(email text references users on delete cascade, courseid uuid references courses on delete cascade,
    primary key (email, courseid));
create table parent_of_at_course(parentemail text references users on delete cascade,
    studentemail text references users on delete cascade, courseid uuid references courses on delete cascade,
    foreign key (studentemail, courseid) references student_at on delete cascade,
    primary key (parentemail, studentemail, courseid));

create table logs(t timestamp, tag text, msg text);
=======

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
    timemodified timestamp NOT NULL CHECK (timemodified >= timeadded),
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

>>>>>>> dev
