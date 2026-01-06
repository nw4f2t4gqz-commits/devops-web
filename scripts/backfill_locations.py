#!/usr/bin/env python3
"""
Backfill access locations by scanning Lead.ip addresses and updating AccessLocation counts.
Run from project root: python3 scripts/backfill_locations.py
Requires the same environment as the app (LEADS_DB path or use default data/leads.db).
"""
import os
import sys
import datetime
from pathlib import Path
# Ensure project root is on sys.path so we can import models and app
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from models import SessionLocal, Lead, AccessLocation
from app import get_country_for_ip


def main():
    s = SessionLocal()
    try:
        print('Scanning leads to rebuild location stats...')
        counts = {}
        total = 0
        for lead in s.query(Lead).all():
            total += 1
            ip = (lead.ip or '').strip()
            if not ip:
                country = 'OTHER'
            else:
                country = get_country_for_ip(ip) or ''
                if not country:
                    # Use Accept-Language is not available here; mark as OTHER
                    country = 'OTHER'
            counts[country] = counts.get(country, 0) + 1
        print(f'Processed {total} leads, found {len(counts)} countries')

        # Clear existing access location table
        print('Clearing existing AccessLocation rows...')
        s.query(AccessLocation).delete()
        s.commit()

        now = datetime.datetime.utcnow()
        for country, cnt in counts.items():
            al = AccessLocation(country=country, count=cnt, first_seen=now, last_seen=now)
            s.add(al)
        s.commit()
        print('Backfill complete.')
    except Exception as e:
        print('Error during backfill:', e)
        s.rollback()
    finally:
        s.close()


if __name__ == '__main__':
    main()
