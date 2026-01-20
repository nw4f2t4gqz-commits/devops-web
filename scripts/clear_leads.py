#!/usr/bin/env python3
"""Small maintenance script to safely clear all rows from the Lead table.

Usage:
  ./scripts/clear_leads.py         # interactive, asks for confirmation
  ./scripts/clear_leads.py --yes   # runs non-interactively

The script will first create a timestamped backup copy of the SQLite file (data/leads.db)
into the same directory named leads.db.YYYYmmdd_HHMMSS.bak.

It uses the project's SQLAlchemy SessionLocal and Lead model.
"""
import os
import shutil
import datetime
import argparse
import sys

# Ensure we can import models from project root
HERE = os.path.dirname(os.path.dirname(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

try:
    from models import SessionLocal, Lead, AccessLocation
except Exception as e:
    print("Failed to import models. Run this script from the project root and ensure dependencies are installed.")
    raise

DB_FILE = os.path.join(HERE, 'data', 'leads.db')

parser = argparse.ArgumentParser(description='Clear all leads from the SQLite DB (with backup).')
parser.add_argument('--yes', action='store_true', help='Do not ask for confirmation')
args = parser.parse_args()

if not os.path.exists(DB_FILE):
    print(f"DB file not found: {DB_FILE}")
    sys.exit(1)

# Backup creation disabled per request — script will NOT create a backup copy of the DB.
# If you need backups in the future, re-enable the code below or run an external backup.

if not args.yes:
    confirm = input('This will DELETE ALL rows from the leads table. Type YES to proceed: ')
    if confirm.strip() != 'YES':
        print('Aborted by user. Backup preserved.')
        sys.exit(0)

# Perform deletion using SQLAlchemy
session = SessionLocal()
try:
    deleted_leads = session.query(Lead).delete()
    deleted_locs = session.query(AccessLocation).delete()
    session.commit()
    print(f'Deleted {deleted_leads} rows from leads table.')
    print(f'Deleted {deleted_locs} rows from access locations table.')
except Exception as e:
    session.rollback()
    print('Failed to clear leads:', e)
finally:
    session.close()

print('Done. No backup was created (backups disabled).')
