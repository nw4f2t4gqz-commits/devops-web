#!/usr/bin/env python3
"""Simple SMTP tester: reads SMTP_* env vars and tries to send a test message.
Usage: set env vars (or copy .env.template -> .env and `export $(cat .env | xargs)`) and run:
    python scripts/test_smtp.py
"""
import os
import smtplib
from email.message import EmailMessage


def main():
    host = os.environ.get('SMTP_HOST')
    port = int(os.environ.get('SMTP_PORT', 587))
    user = os.environ.get('SMTP_USER')
    pw = os.environ.get('SMTP_PASS')
    to = os.environ.get('EMAIL_TO')

    if not (host and user and pw and to):
        print('Missing one of SMTP_HOST/SMTP_USER/SMTP_PASS/EMAIL_TO in env')
        return 2

    msg = EmailMessage()
    msg['Subject'] = 'Testovací email z webu'
    msg['From'] = user
    msg['To'] = to
    msg.set_content('Toto je testovací zpráva. Pokud dorazí, SMTP je nastaveno správně.')

    try:
        with smtplib.SMTP(host, port, timeout=15) as s:
            s.set_debuglevel(1)
            s.starttls()
            s.login(user, pw)
            s.send_message(msg)
        print('OK: email sent')
        return 0
    except Exception as e:
        import traceback
        traceback.print_exc()
        print('FAILED:', e)
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
