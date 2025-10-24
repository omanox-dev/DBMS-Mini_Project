from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / 'hospital.db'

app = Flask(__name__)
app.secret_key = 'dev-secret'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/patients')
def patients():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM patients ORDER BY last_name, first_name')
    rows = cur.fetchall()
    conn.close()
    return render_template('patients.html', patients=rows)

@app.route('/patients/add', methods=('GET', 'POST'))
def add_patient():
    if request.method == 'POST':
        first = request.form['first_name']
        last = request.form['last_name']
        dob = request.form['dob'] or None
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        insurance = request.form['insurance']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO patients (first_name, last_name, dob, phone, email, address, insurance) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (first, last, dob, phone, email, address, insurance))
        conn.commit()
        conn.close()
        flash('Patient added successfully', 'success')
        return redirect(url_for('patients'))

    return render_template('add_patient.html')

@app.route('/appointments')
def appointments():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT a.appointment_id, a.appointment_datetime, a.status, a.reason,
               p.patient_id, p.first_name AS patient_first, p.last_name AS patient_last,
               d.doctor_id, d.first_name AS doctor_first, d.last_name AS doctor_last
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        ORDER BY a.appointment_datetime
    ''')
    rows = cur.fetchall()
    conn.close()
    return render_template('appointments.html', appointments=rows)

@app.route('/appointments/schedule', methods=('GET', 'POST'))
def schedule_appointment():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT doctor_id, first_name, last_name FROM doctors')
    doctors = cur.fetchall()
    cur.execute('SELECT patient_id, first_name, last_name FROM patients')
    patients = cur.fetchall()

    if request.method == 'POST':
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        appointment_datetime = request.form['appointment_datetime']
        reason = request.form['reason']

        cur.execute('INSERT INTO appointments (patient_id, doctor_id, appointment_datetime, reason) VALUES (?, ?, ?, ?)',
                    (patient_id, doctor_id, appointment_datetime, reason))
        conn.commit()
        conn.close()
        flash('Appointment scheduled', 'success')
        return redirect(url_for('appointments'))

    conn.close()
    return render_template('schedule.html', doctors=doctors, patients=patients)

@app.route('/patient/<int:patient_id>')
def patient_history(patient_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM patients WHERE patient_id = ?', (patient_id,))
    patient = cur.fetchone()

    cur.execute('''
        SELECT v.visit_id, v.visit_date, v.diagnosis, v.notes, d.first_name AS doctor_first, d.last_name AS doctor_last
        FROM visits v JOIN doctors d ON v.doctor_id = d.doctor_id
        WHERE v.patient_id = ?
        ORDER BY v.visit_date DESC
    ''', (patient_id,))
    visits = cur.fetchall()

    cur.execute('''
        SELECT p.prescription_id, p.medication, p.dosage, p.frequency, p.duration, p.prescribed_at
        FROM prescriptions p JOIN visits v ON p.visit_id = v.visit_id
        WHERE v.patient_id = ?
        ORDER BY p.prescribed_at DESC
    ''', (patient_id,))
    prescriptions = cur.fetchall()

    conn.close()
    return render_template('patient_history.html', patient=patient, visits=visits, prescriptions=prescriptions)


@app.route('/patients/delete/<int:patient_id>', methods=('POST',))
def delete_patient(patient_id):
    """Delete a patient and rely on FK cascade to remove related records."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM patients WHERE patient_id = ?', (patient_id,))
    p = cur.fetchone()
    if not p:
        conn.close()
        flash('Patient not found', 'danger')
        return redirect(url_for('patients'))

    cur.execute('DELETE FROM patients WHERE patient_id = ?', (patient_id,))
    conn.commit()
    conn.close()
    flash('Patient and related records deleted', 'success')
    return redirect(url_for('patients'))


@app.route('/reports/billing')
def report_billing():
    """Billing summary: total billed and unpaid amounts per patient"""
    conn = get_db_connection()
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
    rows = cur.fetchall()
    conn.close()
    return render_template('reports/billing.html', rows=rows)


@app.route('/reports/doctor-workload')
def report_doctor_workload():
    """Doctor workload: number of appointments per doctor in the next 7 days"""
    conn = get_db_connection()
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
    rows = cur.fetchall()
    conn.close()
    return render_template('reports/doctor_workload.html', rows=rows)


@app.route('/reports/daily-appointments')
def report_daily_appointments():
    """List appointments for today"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT a.appointment_id, a.appointment_datetime, a.status, p.first_name || ' ' || p.last_name AS patient_name,
               d.first_name || ' ' || d.last_name AS doctor_name
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE date(a.appointment_datetime) = date('now')
        ORDER BY a.appointment_datetime
    ''')
    rows = cur.fetchall()
    conn.close()
    return render_template('reports/daily_appointments.html', rows=rows)


@app.route('/reports/overdue-bills')
def report_overdue_bills():
    """Show unpaid bills older than 30 days"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT b.bill_id, b.issued_at, b.amount, b.status, p.first_name || ' ' || p.last_name AS patient_name
        FROM bills b
        JOIN patients p ON b.patient_id = p.patient_id
        WHERE b.status = 'unpaid' AND date(b.issued_at) <= date('now', '-30 days')
        ORDER BY b.issued_at
    ''')
    rows = cur.fetchall()
    conn.close()
    return render_template('reports/overdue_bills.html', rows=rows)

if __name__ == '__main__':
    # auto-init DB if missing
    if not DB_PATH.exists():
        from init_db import init_db
        init_db()
    app.run(debug=True)
