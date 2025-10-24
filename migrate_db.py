"""Migration script: add trigger to auto-create a bill when a visit is inserted."""
import sqlite3
from pathlib import Path

DB = Path(__file__).parent / 'hospital.db'

SQL_TRIGGER = '''
CREATE TRIGGER IF NOT EXISTS trg_create_bill_after_visit
AFTER INSERT ON visits
BEGIN
    INSERT INTO bills (visit_id, patient_id, amount, status)
    VALUES (NEW.visit_id, NEW.patient_id, 50.0, 'unpaid');
END;
'''

def apply_migration(db_path=DB):
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript(SQL_TRIGGER)
    conn.commit()
    conn.close()
    print("Migration applied: trigger trg_create_bill_after_visit created (if not existed)")

if __name__ == '__main__':
    apply_migration()
