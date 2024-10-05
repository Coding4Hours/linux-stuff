import sqlite3

DB_FILE = "search_engine.db"


def print_table_schema():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("PRAGMA table_info(documents);")
    schema = c.fetchall()
    conn.close()

    for column in schema:
        print(column)


if __name__ == "__main__":
    print_table_schema()
