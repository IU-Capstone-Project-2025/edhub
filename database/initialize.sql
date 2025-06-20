create database edhub;
\c edhub
CREATE TABLE File(
    id uuid PRIMARY KEY,
    size int NOT NULL
);

CREATE TABLE FileWithName(
    fileid uuid PRIMARY KEY REFERENCES File ON DELETE CASCADE,
    filename varchar(128) NOT NULL
);

CREATE TABLE Account(
    login varchar(128) PRIMARY KEY,
    passwordhash bytea NOT NULL CHECK (octet_length(passwordhash) = 32),
    publicname varchar(128) NOT NULL,
    timeregistered timestamp NOT NULL,
    contactinfo text NOT NULL CHECK (length(contactinfo) <= 1000),
    avatar uuid NULL REFERENCES File,
    institutional bool NOT NULL DEFAULT 'f', -- managed by the admin if true
    verified bool NOT NULL DEFAULT 'f'
);

CREATE TYPE GradingScheme AS ENUM('average', 'sum');

CREATE TABLE Course(
    id uuid PRIMARY KEY,
    timecreated timestamp NOT NULL,
    name varchar(128) NOT NULL,
    totalgradeenabled bool NOT NULL DEFAULT 'f',
    coursegradingscheme GradingScheme NOT NULL
    -- uses CourseGradeThresholds if coursegradingscheme = 'sum'
);

CREATE TABLE CourseGradeThresholds(
    courseid uuid NOT NULL REFERENCES Course ON DELETE CASCADE,
    threshold int NOT NULL CHECK (threshold >= 0),
    grade varchar(32) NOT NULL
);

CREATE TABLE CourseAnnouncement(
    courseid uuid NOT NULL REFERENCES Course ON DELETE CASCADE,
    annid uuid NOT NULL,
    author varchar(128) NULL REFERENCES Account ON DELETE SET NULL,
    timecreated timestamp NOT NULL,
    title text NOT NULL CHECK (length(title) <= 100),
    content text NOT NULL CHECK (length(content) <= 1000),
    PRIMARY KEY (courseid, annid)
);

CREATE TYPE CourseItemKind AS ENUM('material', 'assignment', 'customgrade');

CREATE TABLE CourseItem(
    courseid uuid NOT NULL REFERENCES Course ON DELETE CASCADE,
    itemid uuid NOT NULL,
    ordering int NOT NULL,
    timecreated timestamp NOT NULL,
    title text NOT NULL CHECK (length(title) <= 100),
    kind CourseItemKind NOT NULL,
    comment text NOT NULL CHECK (length(comment) <= 1000),
    PRIMARY KEY (courseid, itemid)
);

-- MaterialCourseItem would have nothing extra, so not defined

CREATE TABLE AssignmentCourseItem( -- extends CourseItem
    courseid uuid NOT NULL,
    itemid uuid NOT NULL,
    maxpoints int NULL CHECK (maxpoints IS NULL OR maxpoints >= 0),
    PRIMARY KEY (courseid, itemid),
    FOREIGN KEY (courseid, itemid) REFERENCES CourseItem ON DELETE CASCADE
);

CREATE TABLE AssignmentCriterion(
    courseid uuid NOT NULL,
    itemid uuid NOT NULL,
    points int NOT NULL, -- sorted by this
    comment text NOT NULL CHECK (length(comment) <= 200),
    PRIMARY KEY (courseid, itemid, points),
    FOREIGN KEY (courseid, itemid) REFERENCES AssignmentCourseItem
);

CREATE TABLE CustomGradeCourseItem( -- extends CourseItem
    courseid uuid NOT NULL,
    itemid uuid NOT NULL,
    maxpoints int NULL CHECK (maxpoints IS NULL OR maxpoints >= 0),
    PRIMARY KEY (courseid, itemid),
    FOREIGN KEY (courseid, itemid) REFERENCES CourseItem ON DELETE CASCADE
);

CREATE TABLE CourseItemAttachment(
    courseid uuid NOT NULL,
    itemid uuid NOT NULL,
    file uuid NOT NULL REFERENCES FileWithName ON DELETE RESTRICT,
    FOREIGN KEY (courseid, itemid) REFERENCES CourseItem ON DELETE CASCADE
);

create table course_assignments_submissions(courseid uuid references courses on
    delete cascade, assid int references course_assignments on delete cascade,
    email text references users on delete cascade, timeadded timestamp,
    timemodified timestamp, comment text, grade int, gradedby text references
    users on delete set null, primary key (courseid, assid, email));

CREATE TABLE AssignmentSubmission(
    courseid uuid NOT NULL REFERENCES Course ON DELETE CASCADE,
    itemid uuid NOT NULL REFERENCES AssignmentCourseItem ON DELETE CASCADE,
    submittedby varchar(128) NOT NULL REFERENCES Account ON DELETE CASCADE,
    timecreated timestamp NOT NULL,
    timemodified timestamp NOT NULL,
    comment text NOT NULL CHECK (length(comment) <= 65536),
    PRIMARY KEY (courseid, itemid, submittedby)
);

CREATE TABLE AssignmentGrade(
    courseid uuid NOT NULL REFERENCES Course ON DELETE CASCADE,
    itemid uuid NOT NULL REFERENCES AssignmentCourseItem ON DELETE CASCADE,
    submittedby varchar(128) NOT NULL REFERENCES Account ON DELETE CASCADE,
    grade int NOT NULL,
    timecreated timestamp NOT NULL,
    -- gradestale bool = AssignmentGrade.timecreated < AssignmentSubmission.timemodified
    comment text NULL CHECK (comment IS NULL OR length(comment) <= 1024),
    PRIMARY KEY (courseid, itemid, submittedby),
    FOREIGN KEY (courseid, itemid, submittedby) REFERENCES AssignmentSubmission ON DELETE CASCADE
);

CREATE TABLE Notification(
    id uuid PRIMARY KEY,
    read bool NOT NULL DEFAULT 'f',
    timesent timestamp NOT NULL,
    recipient varchar(128) NOT NULL REFERENCES Account ON DELETE CASCADE
);

CREATE TYPE InvitationKind AS ENUM ('student', 'teacher', 'parent');

CREATE TABLE CourseInvitation( -- extends notification
    id uuid PRIMARY KEY REFERENCES Notification ON DELETE CASCADE,
    timeexpires timestamp NOT NULL,
    courseid uuid NOT NULL REFERENCES Course ON DELETE CASCADE,
    kind InvitationKind NOT NULL
);

CREATE TABLE StudentInvitation( -- extends courseinvitation
    id uuid PRIMARY KEY REFERENCES CourseInvitation ON DELETE CASCADE
);

CREATE TABLE TeacherInvitation( -- extends courseinvitation
    id uuid PRIMARY KEY REFERENCES CourseInvitation ON DELETE CASCADE
);

CREATE TABLE ParentInvitation( -- extends courseinvitation
    id uuid PRIMARY KEY REFERENCES Courseinvitation ON DELETE CASCADE,
    studentid varchar(128) NULL REFERENCES Account ON DELETE SET NULL
);

CREATE TABLE StudentAt(
    studentlogin varchar(128) NOT NULL REFERENCES Account ON DELETE CASCADE,
    courseid uuid NOT NULL REFERENCES Course ON DELETE CASCADE,
    PRIMARY KEY (studentlogin, courseid)
);

CREATE TABLE TeacherAt(
    teacherlogin varchar(128) NOT NULL REFERENCES Account ON DELETE CASCADE,
    courseid uuid NOT NULL REFERENCES Course ON DELETE CASCADE,
    PRIMARY KEY (teacherlogin, courseid)
);

CREATE TABLE ParentOfAt(
    parentlogin varchar(128) NOT NULL REFERENCES Account ON DELETE CASCADE,
    studentlogin varchar(128) NOT NULL REFERENCES Account ON DELETE CASCADE,
    courseid uuid NOT NULL REFERENCES Course ON DELETE CASCADE,
    PRIMARY KEY (parentlogin, studentlogin, courseid),
    FOREIGN KEY (studentlogin, courseid) REFERENCES StudentAt ON DELETE CASCADE
);
