import sqlite3

DB_FILE = "search_engine.db"


def update_database_schema():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Create a new table with the desired schema
    c.execute("""
        CREATE TABLE IF NOT EXISTS documents_new (
            doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            title TEXT,
            content TEXT
        )
    """)

    # Copy data from the old table to the new table
    c.execute("""
        INSERT INTO documents_new (url, title, content)
        SELECT url, title, content FROM documents
    """)

    # Drop the old table
    c.execute("DROP TABLE documents")

    # Rename the new table to the old table's name
    c.execute("ALTER TABLE documents_new RENAME TO documents")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    update_database_schema()
