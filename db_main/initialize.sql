create database edhub;
\c edhub
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
