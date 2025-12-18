PRAGMA foreign_keys = ON;
-- PRAGMA journal_mode = WAL;

CREATE TABLE kv_store (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE CHECK (username = lower(username) AND length(username) BETWEEN 1 AND 64),
    name TEXT NOT NULL CHECK (length(name) BETWEEN 1 AND 64),
    password TEXT NOT NULL
);

CREATE TABLE access (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK (name = lower(name))
);

CREATE TABLE r_user_access (
    id INTEGER PRIMARY KEY,
    user INTEGER NOT NULL UNIQUE REFERENCES user(id) ON DELETE CASCADE,
    access INTEGER NOT NULL UNIQUE REFERENCES access(id) ON DELETE CASCADE
);

CREATE TABLE user_session (
    id INTEGER PRIMARY KEY,
    user INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    last_active INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);