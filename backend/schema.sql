PRAGMA foreign_keys = ON;
PRAGMA synchronous = FULL;
-- PRAGMA journal_mode = WAL;

CREATE TABLE kv_store (
    id INTEGER PRIMARY KEY UNIQUE NOT NULL,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL
);

CREATE TABLE user (
    id INTEGER PRIMARY KEY UNIQUE NOT NULL,
    username TEXT NOT NULL UNIQUE CHECK (username = lower(username) AND length(username) BETWEEN 1 AND 64),
    name TEXT NOT NULL CHECK (length(name) BETWEEN 1 AND 64),
    password TEXT NOT NULL
);

CREATE TABLE access (
    id INTEGER PRIMARY KEY UNIQUE NOT NULL,
    name TEXT NOT NULL UNIQUE CHECK (name = lower(name))
);

CREATE TABLE r_user_access (
    id INTEGER PRIMARY KEY UNIQUE NOT NULL,
    user INTEGER NOT NULL UNIQUE REFERENCES user(id) ON UPDATE CASCADE ON DELETE CASCADE,
    access INTEGER NOT NULL UNIQUE REFERENCES access(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE user_session (
    id INTEGER PRIMARY KEY UNIQUE NOT NULL,
    user INTEGER NOT NULL REFERENCES user(id) ON UPDATE CASCADE ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    last_active INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);

CREATE TABLE zis_payment (
    id INTEGER PRIMARY KEY UNIQUE NOT NULL,
    uuid TEXT UNIQUE NOT NULL
);

CREATE TABLE zis_payment_version (
    id INTEGER PRIMARY KEY UNIQUE NOT NULL,
    payment INTEGER NOT NULL REFERENCES zis_payment(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    version INTEGER NOT NULL,
    payer_name TEXT NOT NULL,
    payer_number TEXT,
    payer_email TEXT,
    payer_address TEXT NOT NULL,
    note TEXT,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    created_by INTEGER NOT NULL REFERENCES user(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    is_deleted INTEGER NOT NULL DEFAULT FALSE CHECK (is_deleted IN (TRUE, FALSE)),
    CONSTRAINT number_or_email_required CHECK (payer_number IS NOT NULL OR payer_email IS NOT NULL),
    UNIQUE (payment, version)
);

CREATE TABLE zis_payment_category (
    id INTEGER PRIMARY KEY UNIQUE NOT NULL,
    name TEXT NOT NULL UNIQUE CHECK (name = lower(name))
);

CREATE TABLE zis_payment_line (
    id INTEGER PRIMARY KEY UNIQUE NOT NULL,
    payment_version INTEGER NOT NULL REFERENCES zis_payment_version(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    payer_name TEXT NOT NULL,
    category INTEGER NOT NULL REFERENCES zis_payment_category(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    amount INTEGER NOT NULL CHECK (amount >= 0),
    note TEXT
);