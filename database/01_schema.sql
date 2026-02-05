DROP TABLE IF EXISTS books CASCADE;

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100) NOT NULL,
    isbn VARCHAR(34) UNIQUE NOT NULL,
    published_year INTEGER,
    available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_books_isbn ON books(isbn);

CREATE INDEX idx_books_author ON books(author);