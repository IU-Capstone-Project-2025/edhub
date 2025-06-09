create database edhub;
\c edhub
create table users(email text primary key, publicname text, isadmin bool, timeregistered timestamp, passwordhash text);
create table courses(courseid uuid primary key, name text, timecreated timestamp);
create table course_materials(courseid uuid references courses, matid serial, timeadded timestamp,
    name text, description text, primary key (courseid, matid));
create table course_materials_attachments(courseid uuid, matid int, name text,
    filepath text, foreign key (courseid, matid) references course_materials,
    primary key (courseid, matid, name));
create table teaches(email text references users, courseid uuid references courses,
    primary key (email, courseid));
create table student_at(email text references users, courseid uuid references courses,
    primary key (email, courseid));
create table parent_of_at_course(parentemail text references users,
    studentemail text references users, courseid uuid references courses,
    primary key (parentemail, studentemail, courseid));
