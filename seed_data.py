import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random

HERE = Path(__file__).parent
DB_PATH = HERE / 'hospital.db'


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn


def ensure_schema():
    # If DB is missing, call init_db to create schema-only DB
    if not DB_PATH.exists():
        from init_db import init_db
        init_db()


def apply_migration():
    # ensure trigger exists
    from migrate_db import apply_migration as mapply
    mapply()


def seed_departments(conn):
    depts = [
        ('General Medicine', 'Building A'),
        ('Pediatrics', 'Building B'),
        ('Cardiology', 'Building C'),
        ('Orthopedics', 'Building D'),
        ('Gynecology', 'Building E'),
    ]
    cur = conn.cursor()
    cur.executemany('INSERT INTO departments (name, location) VALUES (?, ?)', depts)
    conn.commit()


def seed_medications(conn):
    meds = [
        ('Paracetamol', 'Analgesic/antipyretic'),
        ('Amoxicillin', 'Antibiotic'),
        ('Metformin', 'Antidiabetic'),
        ('Amlodipine', 'Antihypertensive'),
        ('Lisinopril', 'ACE inhibitor'),
        ('Azithromycin', 'Antibiotic'),
        ('Cetirizine', 'Antihistamine'),
        ('Omeprazole', 'Proton-pump inhibitor'),
        ('Atorvastatin', 'Statin'),
        ('Metoprolol', 'Beta blocker'),
    ]
    cur = conn.cursor()
    cur.executemany('INSERT INTO medications (name, description) VALUES (?, ?)', meds)
    conn.commit()


def seed_doctors(conn):
    # 10 Indian doctor names with specialties
    doctors = [
        ('Amit', 'Sharma', 'General Physician', '9876500001', 'amit.sharma@example.in', 1),
        ('Priya', 'Verma', 'Pediatrician', '9876500002', 'priya.verma@example.in', 2),
        ('Rahul', 'Kumar', 'Cardiologist', '9876500003', 'rahul.kumar@example.in', 3),
        ('Sneha', 'Patel', 'Orthopedic', '9876500004', 'sneha.patel@example.in', 4),
        ('Vikram', 'Singh', 'Gynecologist', '9876500005', 'vikram.singh@example.in', 5),
        ('Neha', 'Reddy', 'General Physician', '9876500006', 'neha.reddy@example.in', 1),
        ('Suresh', 'Ganesan', 'Cardiologist', '9876500007', 'suresh.ganesan@example.in', 3),
        ('Anjali', 'Kaur', 'Pediatrician', '9876500008', 'anjali.kaur@example.in', 2),
        ('Rohit', 'Mehta', 'Orthopedic', '9876500009', 'rohit.mehta@example.in', 4),
        ('Isha', 'Das', 'General Physician', '9876500010', 'isha.das@example.in', 1),
    ]
    cur = conn.cursor()
    cur.executemany('INSERT INTO doctors (first_name, last_name, specialty, phone, email, department_id) VALUES (?, ?, ?, ?, ?, ?)', doctors)
    conn.commit()


def seed_patients(conn):
    # 25 Indian names, with DOBs, contacts
    first_names = ['Arjun','Karan','Sana','Manish','Lakshmi','Rakesh','Sunita','Deepak','Pooja','Ankit','Priyanka','Siddharth','Divya','Kavita','Rohit','Meera','Ananya','Vishal','Shreya','Rajesh','Madhuri','Aakash','Bhavna','Harish','Geeta']
    last_names = ['Shah','Patel','Gupta','Rao','Iyer','Bose','Chopra','Desai','Kapoor','Jain','Nair','Menon','Saxena','Joshi','Malhotra','Trivedi','Nath','Khan','Kohli','Singh','Verma','Bhandari','Goyal','Kumar','Das']
    cur = conn.cursor()
    patients = []
    random.seed(42)
    for i in range(25):
        fn = first_names[i]
        ln = last_names[i]
        # generate DOB between 1945 and 2015
        start = datetime(1945,1,1)
        end = datetime(2015,12,31)
        dob = start + timedelta(days=random.randint(0, (end-start).days))
        dob_str = dob.date().isoformat()
        phone = f'98{random.randint(10000000,99999999)}'
        email = f'{fn.lower()}.{ln.lower()}{i}@example.in'
        address = f'{random.randint(10,200)} MG Road, City'
        insurance = random.choice(['Arogya Care','Bharat Health','None','National Insurance'])
        patients.append((fn, ln, dob_str, phone, email, address, insurance))

    cur.executemany('INSERT INTO patients (first_name, last_name, dob, phone, email, address, insurance) VALUES (?, ?, ?, ?, ?, ?, ?)', patients)
    conn.commit()


def seed_appointments_and_visits(conn):
    cur = conn.cursor()
    # grab patient and doctor ids
    cur.execute('SELECT patient_id FROM patients')
    patients = [r['patient_id'] for r in cur.fetchall()]
    cur.execute('SELECT doctor_id FROM doctors')
    doctors = [r['doctor_id'] for r in cur.fetchall()]
    now = datetime.now()
    visit_ids = []

    # For each patient create 1-3 appointments; some in next 20 days, some in past 60 days
    for pid in patients:
        num_appt = random.choice([1,2,2])
        for _ in range(num_appt):
            doc = random.choice(doctors)
            # Decide future or past
            if random.random() < 0.6:
                # schedule in next 20 days
                dt = now + timedelta(days=random.randint(0,20), hours=random.randint(8,16))
            else:
                # past within 60 days
                dt = now - timedelta(days=random.randint(1,60), hours=random.randint(0,8))

            dt_str = dt.strftime('%Y-%m-%d %H:%M')
            reason = random.choice(['Routine checkup','Fever','Cough','Follow-up','Prescription refill','Pain'])
            cur.execute('INSERT INTO appointments (patient_id, doctor_id, department_id, appointment_datetime, reason, status) VALUES (?, ?, ?, ?, ?, ?)',
                        (pid, doc, None, dt_str, reason, 'scheduled'))
            appt_id = cur.lastrowid

            # For many appointments create a visit (simulate patient attended)
            if random.random() < 0.7:
                visit_date = dt - timedelta(minutes=random.randint(-30,180))
                visit_date_str = visit_date.strftime('%Y-%m-%d %H:%M')
                diagnosis = random.choice(['Hypertension','Diabetes','Viral fever','Upper respiratory infection','Back pain','Gastritis'])
                notes = 'Auto-seeded visit'
                cur.execute('INSERT INTO visits (appointment_id, patient_id, doctor_id, visit_date, diagnosis, notes) VALUES (?, ?, ?, ?, ?, ?)',
                            (appt_id, pid, doc, visit_date_str, diagnosis, notes))
                vid = cur.lastrowid
                visit_ids.append((vid, visit_date))

    conn.commit()
    return visit_ids


def seed_prescriptions_and_adjust_bills(conn, visit_ids):
    cur = conn.cursor()
    # get med ids
    cur.execute('SELECT med_id FROM medications')
    meds = [r['med_id'] for r in cur.fetchall()]

    overdue_count = 0
    for vid, visit_dt in visit_ids:
        # Attach 0-2 prescriptions
        if random.random() < 0.8:
            num_rx = random.choice([1,1,2])
            for _ in range(num_rx):
                med = random.choice(meds)
                med_name = None
                cur.execute('SELECT name FROM medications WHERE med_id = ?', (med,))
                row = cur.fetchone()
                if row:
                    med_name = row['name']
                dosage = random.choice(['500 mg','10 mg','5 mg','1 tablet'])
                frequency = random.choice(['once daily','twice daily','three times daily'])
                duration = random.choice(['5 days','7 days','10 days','30 days'])
                cur.execute('INSERT INTO prescriptions (visit_id, med_id, medication, dosage, frequency, duration) VALUES (?, ?, ?, ?, ?, ?)',
                            (vid, med, med_name, dosage, frequency, duration))

        # The bill for this visit was auto-created by trigger; update some bills to be old/unpaid
        cur.execute('SELECT bill_id FROM bills WHERE visit_id = ?', (vid,))
        b = cur.fetchone()
        if b:
            bill_id = b['bill_id']
            # If visit date more than 30 days ago, make bill overdue (issued_at = visit_dt)
            if (datetime.now() - visit_dt).days > 30:
                issued_at = visit_dt - timedelta(days=1)
                issued_at_str = issued_at.strftime('%Y-%m-%d %H:%M:%S')
                cur.execute('UPDATE bills SET issued_at = ?, status = ? WHERE bill_id = ?', (issued_at_str, 'unpaid', bill_id))
                overdue_count += 1
            else:
                # Randomly mark some as paid
                if random.random() < 0.4:
                    paid_at = datetime.now() - timedelta(days=random.randint(0,5))
                    paid_at_str = paid_at.strftime('%Y-%m-%d %H:%M:%S')
                    cur.execute('UPDATE bills SET status = ?, paid_at = ? WHERE bill_id = ?', ('paid', paid_at_str, bill_id))

    conn.commit()
    return overdue_count


def make_report(conn, out_path=HERE / 'seed_report.txt'):
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) as cnt FROM patients')
    patients = cur.fetchone()['cnt']
    cur.execute('SELECT COUNT(*) as cnt FROM doctors')
    doctors = cur.fetchone()['cnt']
    cur.execute('SELECT COUNT(*) as cnt FROM appointments')
    appts = cur.fetchone()['cnt']
    cur.execute('SELECT COUNT(*) as cnt FROM visits')
    visits = cur.fetchone()['cnt']
    cur.execute('SELECT COUNT(*) as cnt FROM prescriptions')
    rx = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt, SUM(amount) as total FROM bills")
    bres = cur.fetchone()
    bills = bres['cnt'] or 0
    total_billed = bres['total'] or 0.0
    cur.execute("SELECT COUNT(*) as cnt, SUM(amount) as total FROM bills WHERE status='unpaid' AND date(issued_at) <= date('now','-30 days')")
    overdue = cur.fetchone()
    overdue_count = overdue['cnt'] or 0
    overdue_amount = overdue['total'] or 0.0

    txt = []
    txt.append(f'Seed summary generated at: {datetime.now().isoformat()}')
    txt.append(f'Patients: {patients}')
    txt.append(f'Doctors: {doctors}')
    txt.append(f'Appointments: {appts}')
    txt.append(f'Visits: {visits}')
    txt.append(f'Prescriptions: {rx}')
    txt.append(f'Bills: {bills} (total amount: {total_billed:.2f})')
    txt.append(f'Overdue bills (>30 days): {overdue_count} (amount: {overdue_amount:.2f})')

    out = '\n'.join(txt)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(out)

    print(out)


def main():
    print('Seeding database with mock hospital data...')
    ensure_schema()
    apply_migration()
    conn = get_conn()
    seed_departments(conn)
    seed_medications(conn)
    seed_doctors(conn)
    seed_patients(conn)
    visit_ids = seed_appointments_and_visits(conn)
    overdue_count = seed_prescriptions_and_adjust_bills(conn, visit_ids)
    make_report(conn)
    conn.close()
    print('Seeding complete.')


if __name__ == '__main__':
    main()
