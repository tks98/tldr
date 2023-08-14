CREATE TABLE summaries (
    id INTEGER PRIMARY KEY,
    pdf_hash TEXT NOT NULL UNIQUE,
    summary TEXT NOT NULL
);
