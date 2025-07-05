CREATE DATABASE edhub_storage;
\c edhub_storage
CREATE TABLE files(
    id uuid PRIMARY KEY,
    content bytea NOT NULL
);
