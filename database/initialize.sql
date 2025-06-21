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

CREATE TYPE GradingScheme AS ENUM('disabled', 'average', 'sum', 'manual');

CREATE TABLE Course(
    id uuid PRIMARY KEY,
    timecreated timestamp NOT NULL,
    name varchar(128) NOT NULL,
    coursegradingscheme GradingScheme NOT NULL DEFAULT 'disabled'
    -- uses CourseGradeThresholds if there are any and coursegradingscheme IN ('average', 'sum')
    -- uses CourseManualGrade and CourseGradeCriterion if coursegradingscheme = 'manual'
);

CREATE TABLE CourseGradeThresholds(
    courseid uuid NOT NULL REFERENCES Course ON DELETE CASCADE,
    threshold int NOT NULL CHECK (threshold >= 0),
    grade varchar(32) NOT NULL,
    PRIMARY KEY (courseid, grade)
);

CREATE TABLE CourseManualGrade(
    courseid uuid NOT NULL REFERENCES Course ON DELETE CASCADE,
    studentlogin varchar(128) NOT NULL REFERENCES Account ON DELETE CASCADE,
    grade varchar(32) NOT NULL,
    PRIMARY KEY (courseid, studentlogin)
);

CREATE TABLE CourseGradeCriterion(
    courseid uuid NOT NULL REFERENCES Course ON DELETE CASCADE,
    grade varchar(128) NOT NULL,
    comment text NOT NULL CHECK (length(comment) <= 1024),
    PRIMARY KEY (courseid, grade)
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

CREATE TYPE CourseItemKind AS ENUM('material', 'gradeable');

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

CREATE TABLE GradeableCourseItem( -- extends CourseItem
    courseid uuid NOT NULL,
    itemid uuid NOT NULL,
    maxpoints int NULL CHECK (maxpoints IS NULL OR maxpoints >= 0),
    assignment bool NOT NULL,  -- true if accepts submissions
    PRIMARY KEY (courseid, itemid),
    FOREIGN KEY (courseid, itemid) REFERENCES CourseItem ON DELETE CASCADE
);

CREATE TABLE CourseItemGradeCriterion(
    courseid uuid NOT NULL,
    itemid uuid NOT NULL,
    points int NOT NULL, -- sorted by this
    comment text NOT NULL CHECK (length(comment) <= 200),
    PRIMARY KEY (courseid, itemid, points),
    FOREIGN KEY (courseid, itemid) REFERENCES GradeableCourseItem ON DELETE CASCADE
);

CREATE TABLE CourseItemAttachment(
    courseid uuid NOT NULL,
    itemid uuid NOT NULL,
    file uuid NOT NULL REFERENCES FileWithName ON DELETE RESTRICT,
    FOREIGN KEY (courseid, itemid) REFERENCES CourseItem ON DELETE CASCADE
);

CREATE TABLE AssignmentSubmission(
    courseid uuid NOT NULL REFERENCES Course ON DELETE CASCADE,
    itemid uuid NOT NULL,
    submittedby varchar(128) NOT NULL REFERENCES Account ON DELETE CASCADE,
    timecreated timestamp NOT NULL,
    timemodified timestamp NOT NULL,
    comment text NOT NULL CHECK (length(comment) <= 65536),
    PRIMARY KEY (courseid, itemid, submittedby),
    FOREIGN KEY (courseid, itemid) REFERENCES GradeableCourseItem ON DELETE CASCADE
);

CREATE TABLE CourseItemGrade(
    courseid uuid NOT NULL REFERENCES Course ON DELETE CASCADE,
    itemid uuid NOT NULL,
    studentlogin varchar(128) NOT NULL REFERENCES Account ON DELETE CASCADE,
    grade int NOT NULL,
    gradedby varchar(128) NULL REFERENCES Account ON DELETE SET NULL,
    timecreated timestamp NOT NULL,
    -- gradestale bool = ItemGrade.timecreated < AssignmentSubmission.timemodified
    comment text NOT NULL CHECK (length(comment) <= 1024),
    PRIMARY KEY (courseid, itemid, studentlogin),
    FOREIGN KEY (courseid, itemid) REFERENCES GradeableCourseItem ON DELETE CASCADE
    -- cannot reference AssignmentSubmission because GradeableCourseItem are also gradeable
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
