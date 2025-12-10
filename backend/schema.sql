PRAGMA foreign_keys = ON;
PRAGMA journal_mode=WAL;

CREATE TABLE user (
    id INTEGER PRIMARY KEY NOT NULL,
    username TEXT NOT NULL UNIQUE CHECK (username = lower(username)),
    name TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE access (
    id INTEGER PRIMARY KEY NOT NULL,
    akses TEXT NOT NULL CHECK (akses = lower(akses))
);

CREATE TABLE r_akses_user (
    id INTEGER PRIMARY KEY NOT NULL,
    user INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    akses INTEGER NOT NULL REFERENCES access(id) ON DELETE CASCADE,
    UNIQUE (user, akses)
);