create database edhub_attachments;
\c edhub_attachments
create table material_files(courseid uuid, matid text, fileid serial,
    foreign key (courseid, matid) references db_main.course_materials(courseid, matid) on delete cascade,
    primary key (courseid, matid, fileid));
create table assignment_files(courseid uuid, assid text, fileid serial,
    foreign key (courseid, assid) references db_main.course_assignments(courseid, assid) on delete cascade,
    primary key (courseid, assid, fileid));
create table submissions_files(courseid uuid, assid text, email text, fileid serial,
    foreign key (courseid, assid, email) references db_main.course_assignments_submissions(courseid, assid, email) on delete cascade,
    primary key (courseid, assid, email, fileid));
