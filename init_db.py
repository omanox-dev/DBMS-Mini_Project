import sqlite3
from pathlib import Path

HERE = Path(__file__).parent
DB_PATH = HERE / 'hospital.db'

def init_db(db_path=DB_PATH):
    if db_path.exists():
        print(f"Database already exists at {db_path}. Overwriting.")
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # enable foreign keys
    cur.execute('PRAGMA foreign_keys = ON;')

    schema_file = HERE / 'schema.sql'

    # apply schema only; do not load sample/seed data by default to keep DB clean
    with schema_file.open('r', encoding='utf-8') as f:
        schema = f.read()
        cur.executescript(schema)

    conn.commit()
    conn.close()
    print(f"Initialized clean database (schema only) at {db_path}")

if __name__ == '__main__':
    init_db()
