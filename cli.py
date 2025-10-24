import click
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'hospital.db'

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn


@click.group()
def cli():
    pass


@cli.command('init-db')
def init_db_cmd():
    """Initialize the SQLite database from schema.sql and data.sql"""
    from init_db import init_db
    init_db()


@cli.command('list-patients')
def list_patients():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT patient_id, first_name, last_name, dob, phone FROM patients ORDER BY last_name')
    rows = cur.fetchall()
    for r in rows:
        click.echo(f"{r['patient_id']:3d}  {r['last_name']}, {r['first_name']}  dob:{r['dob']}  phone:{r['phone']}")
    conn.close()


@cli.command('add-patient')
@click.option('--first', 'first_name', required=True)
@click.option('--last', 'last_name', required=True)
@click.option('--dob', required=False)
@click.option('--phone', required=False)
@click.option('--email', required=False)
@click.option('--address', required=False)
@click.option('--insurance', required=False)
def add_patient_cmd(first_name, last_name, dob, phone, email, address, insurance):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('INSERT INTO patients (first_name, last_name, dob, phone, email, address, insurance) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (first_name, last_name, dob, phone, email, address, insurance))
    conn.commit()
    conn.close()
    click.echo('Patient added')


@cli.command('schedule-appointment')
@click.option('--patient-id', type=int, required=True)
@click.option('--doctor-id', type=int, required=True)
@click.option('--datetime', 'dt', required=True)
@click.option('--reason', required=False, default='')
def schedule_cmd(patient_id, doctor_id, dt, reason):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('INSERT INTO appointments (patient_id, doctor_id, appointment_datetime, reason) VALUES (?, ?, ?, ?)',
                (patient_id, doctor_id, dt, reason))
    conn.commit()
    conn.close()
    click.echo('Appointment scheduled')


@cli.command('patient-history')
@click.argument('patient_id', type=int)
def patient_history_cmd(patient_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM patients WHERE patient_id = ?', (patient_id,))
    p = cur.fetchone()
    if not p:
        click.echo('Patient not found')
        return
    click.echo(f"Patient: {p['first_name']} {p['last_name']} (id {p['patient_id']})")
    click.echo('\nVisits:')
    cur.execute('SELECT visit_id, visit_date, diagnosis FROM visits WHERE patient_id = ? ORDER BY visit_date DESC', (patient_id,))
    for v in cur.fetchall():
        click.echo(f" - {v['visit_date']} id:{v['visit_id']} diag:{v['diagnosis']}")
    click.echo('\nPrescriptions:')
    cur.execute('''
        SELECT pr.prescription_id, pr.medication, pr.dosage, pr.prescribed_at
        FROM prescriptions pr
        JOIN visits v ON pr.visit_id = v.visit_id
        WHERE v.patient_id = ?
    ''', (patient_id,))
    for r in cur.fetchall():
        click.echo(f" - {r['prescribed_at']}: {r['medication']} {r['dosage']}")
    conn.close()
    conn.close()


@cli.command('report-billing')
def cli_report_billing():
    """Print billing summary per patient"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
        SELECT p.patient_id, p.first_name || ' ' || p.last_name AS patient_name,
               SUM(b.amount) AS total_billed,
               SUM(CASE WHEN b.status = 'unpaid' THEN b.amount ELSE 0 END) AS total_unpaid
        FROM bills b
        JOIN patients p ON b.patient_id = p.patient_id
        GROUP BY p.patient_id, patient_name
        ORDER BY total_unpaid DESC
    ''')
    for r in cur.fetchall():
        click.echo(f"{r['patient_id']:3d} {r['patient_name']:30s} billed={r['total_billed'] or 0:.2f} unpaid={r['total_unpaid'] or 0:.2f}")
    conn.close()


@cli.command('report-doctor-workload')
def cli_report_doctor_workload():
    """Print doctor workload (appointments next 7 days)"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
        SELECT d.doctor_id, d.first_name || ' ' || d.last_name AS doctor_name,
               COUNT(a.appointment_id) AS upcoming_appointments
        FROM doctors d
        LEFT JOIN appointments a ON a.doctor_id = d.doctor_id
            AND date(a.appointment_datetime) BETWEEN date('now') AND date('now', '+7 days')
        GROUP BY d.doctor_id, doctor_name
        ORDER BY upcoming_appointments DESC
    ''')
    for r in cur.fetchall():
        click.echo(f"{r['doctor_id']:3d} {r['doctor_name']:25s} upcoming={r['upcoming_appointments']}")
    conn.close()


@cli.command('report-daily-appointments')
def cli_report_daily_appointments():
    """Print today's appointments"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
        SELECT a.appointment_id, a.appointment_datetime, p.first_name || ' ' || p.last_name AS patient_name,
               d.first_name || ' ' || d.last_name AS doctor_name
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE date(a.appointment_datetime) = date('now')
        ORDER BY a.appointment_datetime
    ''')
    for r in cur.fetchall():
        click.echo(f"{r['appointment_id']:3d} {r['appointment_datetime']} {r['patient_name']:25s} -> {r['doctor_name']}")
    conn.close()


@cli.command('report-overdue-bills')
def cli_report_overdue_bills():
    """Print overdue unpaid bills (issued >30 days ago)"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
        SELECT b.bill_id, b.issued_at, b.amount, p.first_name || ' ' || p.last_name AS patient_name
        FROM bills b JOIN patients p ON b.patient_id = p.patient_id
        WHERE b.status = 'unpaid' AND date(b.issued_at) <= date('now', '-30 days')
        ORDER BY b.issued_at
    ''')
    for r in cur.fetchall():
        click.echo(f"{r['bill_id']:3d} {r['issued_at']} {r['patient_name']:25s} amount={r['amount']:.2f}")
    conn.close()

if __name__ == '__main__':
    cli()
