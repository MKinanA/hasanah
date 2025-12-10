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
    name TEXT NOT NULL UNIQUE CHECK (name = lower(name))
);

CREATE TABLE r_user_access (
    id INTEGER PRIMARY KEY NOT NULL,
    user INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    access INTEGER NOT NULL REFERENCES access(id) ON DELETE CASCADE,
    UNIQUE (user, access)
);