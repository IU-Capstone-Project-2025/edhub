create database edhub;
\c edhub
create table users(email text primary key, publicname text, isadmin bool, timeregistered timestamp, passwordhash text);
create table courses(courseid uuid primary key, name text, timecreated timestamp);
create table course_materials(courseid uuid references courses, matid serial, timeadded timestamp, author text,
    name text, description text, primary key (courseid, matid));
create table course_assignments(courseid uuid references courses, assid serial, timeadded timestamp, author text,
    name text, description text, primary key (courseid, assid));
create table course_assignments_submissions(courseid uuid references courses, assid int references course_assignments,
    email text references users, timeadded timestamp, timemodified timestamp, comment text, grade int, gradedby text references users
    primary key (courseid, assid, email));
create table teaches(email text references users, courseid uuid references courses,
    primary key (email, courseid));
create table student_at(email text references users, courseid uuid references courses,
    primary key (email, courseid));
create table parent_of_at_course(parentemail text references users,
    studentemail text references users, courseid uuid references courses,
    primary key (parentemail, studentemail, courseid));
