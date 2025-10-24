#!/usr/bin/env python3
"""Interactive menu-driven CLI for the Healthcare Mini DBMS.

This script wraps the existing `cli.py` commands and exposes them as a
friendly, game-like menu. It calls the current Python interpreter to run
`cli.py` so it works when you run `py -3 interactive_cli.py` on Windows or
`python interactive_cli.py` on other systems.

It intentionally avoids re-implementing database logic: it shells out to
the existing CLI implementation so behavior stays consistent.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
CLI_SCRIPT = ROOT / 'cli.py'


def run_cli(args):
    """Run the cli.py command with given args and return (returncode, stdout, stderr)."""
    cmd = [sys.executable, str(CLI_SCRIPT)] + args
    try:
        res = subprocess.run(cmd, text=True, capture_output=True)
        return res.returncode, res.stdout, res.stderr
    except FileNotFoundError as e:
        return 1, '', f'Failed to run {cmd}: {e}'


def pause():
    input('\nPress Enter to continue...')


def list_patients():
    code, out, err = run_cli(['list-patients'])
    print(out)
    if err:
        print('ERROR:', err)
    pause()


def add_patient():
    print('Add patient (leave blank to skip optional fields)')
    first = input('First name: ').strip()
    last = input('Last name: ').strip()
    dob = input('DOB (YYYY-MM-DD): ').strip()
    phone = input('Phone: ').strip()
    email = input('Email: ').strip()
    address = input('Address: ').strip()
    insurance = input('Insurance: ').strip()
    if not first or not last:
        print('First and last name are required.')
        pause()
        return
    args = ['add-patient', '--first', first, '--last', last]
    if dob:
        args += ['--dob', dob]
    if phone:
        args += ['--phone', phone]
    if email:
        args += ['--email', email]
    if address:
        args += ['--address', address]
    if insurance:
        args += ['--insurance', insurance]

    code, out, err = run_cli(args)
    if out:
        print(out)
    if err:
        print('ERROR:', err)
    pause()


def schedule_appointment():
    print('Schedule appointment')
    try:
        pid = input('Patient ID: ').strip()
        did = input('Doctor ID: ').strip()
        dt = input('Datetime (YYYY-MM-DD HH:MM): ').strip()
        reason = input('Reason (optional): ').strip()
        if not pid or not did or not dt:
            print('Patient ID, Doctor ID and Datetime are required.')
            pause()
            return
        args = ['schedule-appointment', '--patient-id', pid, '--doctor-id', did, '--datetime', dt, '--reason', reason]
        code, out, err = run_cli(args)
        if out:
            print(out)
        if err:
            print('ERROR:', err)
    except Exception as e:
        print('Exception:', e)
    pause()


def patient_history():
    pid = input('Enter patient ID to view history: ').strip()
    if not pid.isdigit():
        print('Invalid patient ID')
        pause()
        return
    code, out, err = run_cli(['patient-history', pid])
    print(out)
    if err:
        print('ERROR:', err)
    pause()


def reports_menu():
    while True:
        print('\nReports')
        print('1) Billing summary')
        print('2) Doctor workload (next 7 days)')
        print("3) Today's appointments")
        print('4) Overdue bills (>30 days)')
        print('0) Back')
        choice = input('Select: ').strip()
        if choice == '1':
            code, out, err = run_cli(['report-billing'])
        elif choice == '2':
            code, out, err = run_cli(['report-doctor-workload'])
        elif choice == '3':
            code, out, err = run_cli(['report-daily-appointments'])
        elif choice == '4':
            code, out, err = run_cli(['report-overdue-bills'])
        elif choice == '0':
            return
        else:
            print('Invalid choice')
            continue
        print(out)
        if err:
            print('ERROR:', err)
        pause()


def init_db():
    print('This will initialize the database (will overwrite existing hospital.db).')
    confirm = input('Type YES to continue: ').strip()
    if confirm == 'YES':
        code, out, err = run_cli(['init-db'])
        print(out)
        if err:
            print('ERROR:', err)
    else:
        print('Cancelled')
    pause()


def main_menu():
    while True:
        print('\n' + '='*60)
        print('Healthcare Mini DBMS — Interactive CLI')
        print('='*60)
        print('1) List patients')
        print('2) Add patient')
        print('3) Schedule appointment')
        print('4) Patient history')
        print('5) Reports')
        print('6) Initialize database (danger)')
        print('0) Exit')
        choice = input('\nSelect an option: ').strip()
        if choice == '1':
            list_patients()
        elif choice == '2':
            add_patient()
        elif choice == '3':
            schedule_appointment()
        elif choice == '4':
            patient_history()
        elif choice == '5':
            reports_menu()
        elif choice == '6':
            init_db()
        elif choice == '0':
            print('Goodbye!')
            break
        else:
            print('Invalid selection. Try again.')


if __name__ == '__main__':
    try:
        main_menu()
    except KeyboardInterrupt:
        print('\nInterrupted — exiting')
