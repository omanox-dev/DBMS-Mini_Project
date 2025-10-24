"""Run quick verification queries and print results to validate reports and trigger."""
import sqlite3
from pathlib import Path

DB = Path(__file__).parent / 'hospital.db'

def run():
    if not DB.exists():
        print(f"Database not found at {DB}")
        return
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    print('\n=== Billing summary (sample) ===')
    cur.execute('''
        SELECT p.first_name || ' ' || p.last_name AS patient_name,
               SUM(b.amount) AS total_billed,
               SUM(CASE WHEN b.status='unpaid' THEN b.amount ELSE 0 END) AS total_unpaid
        FROM bills b JOIN patients p ON b.patient_id = p.patient_id
        GROUP BY p.patient_id
        ORDER BY total_unpaid DESC
        LIMIT 10
    ''')
    for r in cur.fetchall():
        print(f"{r['patient_name']:30s} billed={r['total_billed']:.2f} unpaid={r['total_unpaid']:.2f}")

    print('\n=== Doctor workload (next 7 days) ===')
    cur.execute('''
        SELECT d.first_name || ' ' || d.last_name AS doctor_name,
               COUNT(a.appointment_id) AS upcoming
        FROM doctors d LEFT JOIN appointments a ON a.doctor_id = d.doctor_id
            AND date(a.appointment_datetime) BETWEEN date('now') AND date('now', '+7 days')
        GROUP BY d.doctor_id
        ORDER BY upcoming DESC
    ''')
    for r in cur.fetchall():
        print(f"{r['doctor_name']:25s} upcoming={r['upcoming']}")

    print('\n=== Create a new visit to test trigger (will create a bill) ===')
    # Insert a visit for patient 1 with doctor 1
    cur.execute("INSERT INTO visits (appointment_id, patient_id, doctor_id, visit_date, diagnosis, notes) VALUES (NULL, 1, 1, datetime('now'), 'Check', 'Auto-test')")
    conn.commit()
    # Show last bill
    cur.execute('SELECT bill_id, visit_id, patient_id, amount, status FROM bills ORDER BY bill_id DESC LIMIT 1')
    b = cur.fetchone()
    print(f"New bill: id={b['bill_id']} visit_id={b['visit_id']} patient_id={b['patient_id']} amount={b['amount']} status={b['status']}")

    conn.close()

if __name__ == '__main__':
    run()
