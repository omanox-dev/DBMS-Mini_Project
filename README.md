# Healthcare Medical Organization — Mini DBMS Project

This is a small demo project for a healthcare/medical organization using SQLite as the database, a simple Flask + Bootstrap web UI, and a CLI mode for basic database operations.

What's included
- `schema.sql` — SQL schema (CREATE TABLE statements)
- `data.sql` — sample data inserts
- `init_db.py` — initializes `hospital.db` from `schema.sql` and `data.sql`
- `app.py` — Flask web application (UI: Bootstrap CDN)
- `cli.py` — command-line interface using Click (init-db, add-patient, list-patients, schedule-appointment, patient-history)
- `templates/` — Jinja2 templates for the web UI
- `requirements.txt` — Python packages required

Quick start (Windows PowerShell)

1) Create and activate a Python virtual environment (optional but recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install requirements:

```powershell
pip install -r requirements.txt
```

3) Initialize the database (this creates `hospital.db`):

```powershell
python init_db.py
```

4a) Run the web UI (Flask):

```powershell
python app.py
```

Open http://127.0.0.1:5000 in your browser.

4b) Or use the CLI mode (examples):

```powershell
python cli.py list-patients
python cli.py add-patient --first "Alex" --last "Green" --dob 1990-05-01 --phone "555-0103"
python cli.py schedule-appointment --patient-id 1 --doctor-id 1 --datetime "2025-10-24 10:30" --reason "Checkup"
```
