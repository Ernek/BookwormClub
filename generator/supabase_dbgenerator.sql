-- SQL script to create tables for Supabase from SQLAlchemy models

-- Table: books
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    booktitle VARCHAR(200) NOT NULL,
    bookauthor VARCHAR(200),
    bookimag_url TEXT DEFAULT '/static/images/book_logo.png'
);

-- Table: users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    bio TEXT,
    location TEXT,
    password TEXT NOT NULL
);

-- Table: reads
CREATE TABLE reads (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE
);

