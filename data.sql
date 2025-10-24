-- sample departments
INSERT INTO departments (name, location) VALUES ('General Medicine', 'Building A');
INSERT INTO departments (name, location) VALUES ('Pediatrics', 'Building B');
INSERT INTO departments (name, location) VALUES ('Cardiology', 'Building C');

-- sample doctors
INSERT INTO doctors (first_name, last_name, specialty, phone, email, department_id) VALUES ('John', 'Doe', 'General Physician', '555-0100', 'jdoe@example.com', 1);
INSERT INTO doctors (first_name, last_name, specialty, phone, email, department_id) VALUES ('Lisa', 'Ray', 'Pediatrician', '555-0101', 'lray@example.com', 2);

-- sample patients
INSERT INTO patients (first_name, last_name, dob, gender, phone, email, address, insurance) VALUES ('Alice', 'Smith', '1985-04-12', 'F', '555-0200', 'alice.smith@example.com', '12 Oak St', 'Acme Health');
INSERT INTO patients (first_name, last_name, dob, gender, phone, email, address, insurance) VALUES ('Bob', 'Johnson', '1990-07-23', 'M', '555-0201', 'bob.j@example.com', '34 Pine Rd', 'WellCare');

-- sample appointments
INSERT INTO appointments (patient_id, doctor_id, department_id, appointment_datetime, status, reason) VALUES (1, 1, 1, '2025-10-25 09:00', 'scheduled', 'Routine checkup');
INSERT INTO appointments (patient_id, doctor_id, department_id, appointment_datetime, status, reason) VALUES (2, 2, 2, '2025-10-25 10:30', 'scheduled', 'Fever and cough');

-- sample visits
INSERT INTO visits (appointment_id, patient_id, doctor_id, visit_date, diagnosis, notes) VALUES (1, 1, 1, '2025-10-25 09:05', 'Hypertension - stable', 'Continue current meds');

-- sample medications
INSERT INTO medications (name, description) VALUES ('Paracetamol', 'Analgesic/antipyretic');
INSERT INTO medications (name, description) VALUES ('Lisinopril', 'ACE inhibitor');

-- sample prescriptions
INSERT INTO prescriptions (visit_id, med_id, medication, dosage, frequency, duration) VALUES (1, 2, 'Lisinopril', '10 mg', 'once daily', '30 days');

-- sample bills
INSERT INTO bills (visit_id, patient_id, amount, status) VALUES (1, 1, 75.00, 'unpaid');
