create database edhub_attachments;
\c edhub_attachments
create table users(email text primary key, publicname text, isadmin bool, timeregistered timestamp, passwordhash text);