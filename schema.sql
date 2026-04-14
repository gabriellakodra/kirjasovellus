CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    image BLOB
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT,
    user_id INTEGER REFERENCES users
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    content TEXT,
    sent_at TEXT,
    user_id INTEGER REFERENCES users,
    post_id INTEGER REFERENCES posts
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);

CREATE TABLE post_classes (
    id INTEGER PRIMARY KEY,
    post_id INTEGER REFERENCES posts,
    title TEXT,
    value TEXT
);