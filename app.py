from flask import Flask, render_template, request, jsonify, session
import datetime
import os
import platform
try:
    import requests as _requests
except Exception:
    _requests = None
    import urllib.request as _urllib
    
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import init_db, SessionLocal, Lead
try:
    from flask_wtf import CSRFProtect
    from flask_wtf.csrf import generate_csrf
except Exception:
    # Fallback no-op CSRF if flask_wtf is not installed (prevents import errors while keeping app runnable)
    class _NoopCSRF:
        def __init__(self, *args, **kwargs):
            pass
        def init_app(self, app):
            pass
    CSRFProtect = _NoopCSRF
    def generate_csrf():
        return ''

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')
# Rate limiter: use Redis if REDIS_URL is provided, otherwise fall back to in-memory
redis_url = os.environ.get('REDIS_URL') or os.environ.get('REDIS_URI')
if redis_url:
    app.logger.info(f'Configuring rate limiter to use Redis at {redis_url}')
    limiter = Limiter(key_func=get_remote_address, app=app, default_limits=["200 per day", "50 per hour"], storage_uri=redis_url)
else:
    limiter = Limiter(key_func=get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])

# CSRF protection for POST endpoints (adds protection against cross-site POST requests)
csrf = CSRFProtect()
csrf.init_app(app)

# initialize DB (creates data dir and sqlite file)
init_db()
import logging
from logging.handlers import RotatingFileHandler
import smtplib
from email.message import EmailMessage

# Ensure log directory exists and configure file handler
LOG_DIR = os.path.join(os.path.dirname(__file__), 'log')
os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, 'app.log')

file_handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info(f"Logging initialized. Log file: {log_path}")


@app.route('/')
def home():
    data = {
        "os": platform.system(),
        "release": platform.release(),
        "status": "Healthy",
        "containerized": os.path.exists('/.dockerenv')
    }
    # include deploy_time so footer shows the same info as other pages
    data["deploy_time"] = datetime.datetime.utcnow().isoformat()
    return render_template('index.html', info=data)


def get_client_ip():
    # Respect X-Forwarded-For when behind a proxy
    xff = request.headers.get('X-Forwarded-For', '')
    if xff:
        # X-Forwarded-For can contain a list of IPs
        ip = xff.split(',')[0].strip()
        return ip
    return request.remote_addr


def get_country_for_ip(ip: str) -> str:
    """Return ISO country code for given IP using ipapi.co. Returns empty string on failure."""
    if not ip or ip.startswith('127.') or ip == '::1':
        return ''
    try:
        if _requests is not None:
            resp = _requests.get(f'https://ipapi.co/{ip}/country/', timeout=1.5)
            if resp.status_code == 200:
                return resp.text.strip()
        else:
            # urllib fallback
            try:
                with _urllib.urlopen(f'https://ipapi.co/{ip}/country/', timeout=1.5) as r:
                    data = r.read().decode('utf-8', errors='ignore')
                    return data.strip()
            except Exception:
                pass
    except Exception:
        pass
    return ''


def select_language():
    """Decide language for current request: 'cs' or 'en'.
    Priority: if detected country == 'CZ' use 'cs', else 'en'.
    If geo lookup fails, fallback to Accept-Language header (cs if startswith 'cs').
    Logs the client IP, detected country and selected language.
    """
    ip = get_client_ip()
    country = get_country_for_ip(ip)

    # default
    lang = 'en'
    if country == 'CZ':
        lang = 'cs'
    elif country:
        lang = 'en'
    else:
        # Fallback to Accept-Language
        al = request.headers.get('Accept-Language', '')
        if al.lower().startswith('cs'):
            lang = 'cs'
        else:
            lang = 'en'

    # Log detection result
    try:
        app.logger.info(f"Language selection: ip={ip} country={country!r} lang={lang}")
    except Exception:
        pass

    return lang


translations = {
    'cs': {
        'home': 'Domů',
        'services': 'Služby',
        'about': 'O mně',
        'contact': 'Kontakt',
        'cka': 'Certified Kubernetes Administrator (CKA)',
        'hero_line1': 'Buduji stabilní',
        'hero_highlight': 'Cloud-Native',
        'hero_suffix': 'systémy',
        'hero_paragraph': 'Specializuji se na orchestraci kontejnerů, automatizaci infrastruktury a budování CI/CD pipelines, které zrychlují vývoj.',
        'linkedin': 'LinkedIn',
        'github': 'GitHub',
        'my_expertise': 'Moje Expertíza',
        'bio_title': 'Krátké bio',
        'bio_text': 'Pracuji na DevOps a cloud-native řešeních, specializuji se na Kubernetes (CKA), Terraform a CI/CD. Rád řeším složité provozní problémy a zjednodušuji deploy procesy.',
        'skills_title': 'Dovednosti',
        'contact_me': 'Kontaktovat mě',
        'system_healthy': 'System Healthy'
        , 'deploy': 'Nasazení',
        'admin_login_title': 'Admin přihlášení',
        'admin_login_desc': 'Přihlaste se, abyste spravovali kontaktní záznamy.',
        'username': 'Uživatelské jméno',
        'password': 'Heslo',
        'login': 'Přihlásit'
    },
    'en': {
        'home': 'Home',
        'services': 'Services',
        'admin_login_title': 'Admin login',
        'admin_login_desc': 'Sign in to manage contact leads.',
        'username': 'Username',
        'password': 'Password',
        'login': 'Sign in',
        'about': 'About',
        'contact': 'Contact',
        'cka': 'Certified Kubernetes Administrator (CKA)',
        'hero_line1': 'I build reliable',
        'hero_highlight': 'Cloud-Native',
        'hero_suffix': 'systems',
        'hero_paragraph': 'I specialise in container orchestration, infrastructure automation and building CI/CD pipelines that speed up development.',
        'linkedin': 'LinkedIn',
        'github': 'GitHub',
        'my_expertise': 'My Expertise',
        'bio_title': 'Short bio',
        'bio_text': 'I work on DevOps and cloud-native solutions, specialising in Kubernetes (CKA), Terraform and CI/CD. I enjoy solving complex operational problems and simplifying deploy processes.',
        'skills_title': 'Skills',
        'contact_me': 'Contact me',
        'system_healthy': 'System Healthy'
        , 'deploy': 'Deployment'
    }
}

# expose generate_csrf helper to templates
@app.context_processor
def inject_csrf():
    def csrf_token():
        try:
            return generate_csrf()
        except Exception:
            return ''
    return dict(csrf_token=csrf_token)


@app.context_processor
def inject_translations():
    lang = select_language()

    def tr(key):
        return translations.get(lang, translations['cs']).get(key, key)

    # expose current request path so templates can mark active nav items
    try:
        current_path = request.path
    except Exception:
        current_path = '/'

    admin_enabled = bool(os.environ.get('ADMIN_USER') and os.environ.get('ADMIN_PASS'))
    # expose whether current session is authenticated as admin (session-based login)
    try:
        is_admin = bool(session.get('admin'))
    except Exception:
        is_admin = False
    return dict(tr=tr, current_lang=lang, current_path=current_path, admin_enabled=admin_enabled, is_admin=is_admin)


@app.route('/about')
def about():
    data = {
        "os": platform.system(),
        "release": platform.release(),
        "status": "Healthy",
        "containerized": os.path.exists('/.dockerenv'),
        "deploy_time": datetime.datetime.utcnow().isoformat()
    }
    return render_template('about.html', info=data)


@app.route('/deploy')
def deploy_demo():
    """Render a friendly deployment demo page for visitors.
    It reads local build artifacts (Dockerfile, docker-compose, README) and
    shows the tail of the application log. This is read-only and does not
    execute any build commands on the server — it's only a visual demo.
    """
    data = {
        "os": platform.system(),
        "release": platform.release(),
        "status": "Healthy",
        "containerized": os.path.exists('/.dockerenv'),
        "deploy_time": datetime.datetime.utcnow().isoformat()
    }

    base = os.path.dirname(__file__)

    def read_file_safe(path, max_chars=20000):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) > max_chars:
                    return content[:max_chars] + '\n\n...content truncated...'
                return content
        except Exception:
            return ''

    artifacts = {}
    for fname in ('Dockerfile', 'docker-compose.yml', 'README_DOCKER.md', 'requirements.txt'):
        fp = os.path.join(base, fname)
        artifacts[fname] = {
            'exists': os.path.exists(fp),
            'mtime': datetime.datetime.fromtimestamp(os.path.getmtime(fp)).isoformat() if os.path.exists(fp) else '',
            'content': read_file_safe(fp)
        }

    # tail app log (last N lines) efficiently
    log_fp = os.path.join(LOG_DIR, 'app.log')
    def tail(fpath, n=200):
        try:
            with open(fpath, 'rb') as f:
                f.seek(0, 2)
                end = f.tell()
                block_size = 1024
                data = b''
                while end > 0 and data.count(b'\n') <= n:
                    start = max(0, end - block_size)
                    f.seek(start)
                    data = f.read(end - start) + data
                    end = start
                    block_size *= 2
                lines = data.splitlines()[-n:]
                return '\n'.join([ln.decode('utf-8', errors='replace') for ln in lines])
        except Exception:
            return ''

    logs_tail = tail(log_fp, 200)

    return render_template('deploy.html', info=data, artifacts=artifacts, logs=logs_tail)


@app.route('/contact', methods=['GET', 'POST'])
@limiter.limit("10 per hour")
def contact():
    """Contact form with honeypot and rate limiting. No external email sent by default; logs message."""
    if request.method == 'GET':
        return render_template('contact.html', success=False, error=None)

    # POST
    # Honeypot check
    hp = request.form.get('hp_phone', '')
    if hp:
        app.logger.info(f"Spam blocked by honeypot from {get_client_ip()} (hp={hp})")
        # respond with success status to avoid feeding bots
        return render_template('contact.html', success=True, error=None)

    name = (request.form.get('name') or '').strip()
    email = (request.form.get('email') or '').strip()
    message = (request.form.get('message') or '').strip()

    # basic validation
    if not name or not email or not message:
        return render_template('contact.html', success=False, error='Vyplňte prosím všechna pole.')
    if '@' not in email or ' ' in email:
        return render_template('contact.html', success=False, error='Zadejte platný email.')

    # For now, just log the lead. In production replace with SMTP/SendGrid or similar.
    app.logger.info(f"Contact form submitted: name={name} email={email} from={get_client_ip()} message_len={len(message)}")

    # Persist lead to database
    db_session = None
    try:
        db_session = SessionLocal()
        lead = Lead(name=name, email=email, message=message, ip=get_client_ip())
        db_session.add(lead)
        db_session.commit()
        db_session.refresh(lead)
        app.logger.info(f"Lead persisted id={lead.id}")
    except Exception:
        app.logger.exception('Failed to persist lead to DB')
        if db_session:
            try:
                db_session.rollback()
            except Exception:
                pass

    # Try to send email if SMTP is configured (Office365 or other SMTP)
    smtp_host = os.environ.get('SMTP_HOST')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')
    email_to = os.environ.get('EMAIL_TO')

    if not (smtp_host and smtp_user and smtp_pass and email_to):
        app.logger.warning('SMTP not configured; contact not emailed. Set SMTP_HOST/SMTP_USER/SMTP_PASS/EMAIL_TO')
        return render_template('contact.html', success=False, error='Email není nakonfigurován. Kontakt byl zaznamenán.')

    try:
        msg = EmailMessage()
        msg['Subject'] = f'Kontakt z webu: {name}'
        msg['From'] = smtp_user
        msg['To'] = email_to
        msg['Reply-To'] = email
        body = f"Jméno: {name}\nEmail: {email}\nIP: {get_client_ip()}\n\n{message}"
        msg.set_content(body)

        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as s:
            s.starttls()
            s.login(smtp_user, smtp_pass)
            s.send_message(msg)

        app.logger.info(f'Contact email sent to {email_to} for lead {email}')
        # mark lead emailed
        try:
            if db_session is None:
                db_session = SessionLocal()
            if 'lead' in locals():
                lead.emailed = True
                lead.emailed_at = datetime.datetime.utcnow()
                db_session.add(lead)
                db_session.commit()
        except Exception:
            app.logger.exception('Failed to update lead emailed status')
        return render_template('contact.html', success=True, error=None)
    except Exception as e:
        app.logger.exception(f'Failed to send contact email: {e}')
        # record error on lead
        try:
            if db_session is None:
                db_session = SessionLocal()
            if 'lead' in locals():
                lead.error = str(e)
                db_session.add(lead)
                db_session.commit()
        except Exception:
            app.logger.exception('Failed to record lead error status')
        return render_template('contact.html', success=False, error='Nepodařilo se odeslat email. Zkuste to prosím později.')


@app.route('/health')
def health():
    """Simple health endpoint for probes/monitoring."""
    try:
        resp = {
            "status": "ok",
            "time": datetime.datetime.utcnow().isoformat(),
            "containerized": os.path.exists('/.dockerenv')
        }
        return jsonify(resp), 200
    except Exception:
        return jsonify({"status": "error"}), 500

import os
import base64
import smtplib
import datetime
from functools import wraps
from email.message import EmailMessage
from flask import render_template, request, redirect, url_for, Response, abort

from models import SessionLocal, Lead

def _check_admin(auth_header: str) -> bool:
    if not auth_header:
        return False
    try:
        scheme, token = auth_header.split(None, 1)
        if scheme.lower() != 'basic':
            return False
        decoded = base64.b64decode(token).decode('utf-8', errors='ignore')
        user, pwd = decoded.split(':', 1)
    except Exception:
        return False
    return user == os.environ.get('ADMIN_USER') and pwd == os.environ.get('ADMIN_PASS')

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Prefer session-based login (so admin can explicitly logout).
        try:
            if session.get('admin'):
                return f(*args, **kwargs)
        except Exception:
            # session might not be available in some contexts; fall back to header check
            pass

        auth_header = request.headers.get('Authorization', '')
        # If a Basic auth header is provided, validate it and either allow or challenge
        if auth_header:
            if _check_admin(auth_header):
                return f(*args, **kwargs)
            return Response('Authentication required', 401, {'WWW-Authenticate': 'Basic realm="Admin Area"'})

        # No session and no Basic auth header -> redirect browser to login page
        return redirect(url_for('admin_login', next=request.path))
    return wrapper

def send_contact_email_from_lead(lead: Lead):
    """Pošle email pro záznam Lead; vyhazuje výjimku při selhání."""
    SMTP_HOST = os.environ.get('SMTP_HOST')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USER = os.environ.get('SMTP_USER')
    SMTP_PASS = os.environ.get('SMTP_PASS')
    EMAIL_TO = os.environ.get('EMAIL_TO')
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS and EMAIL_TO):
        raise RuntimeError("SMTP not configured")

    msg = EmailMessage()
    msg['Subject'] = f'Kontakt z webu: {lead.name}'
    msg['From'] = SMTP_USER
    msg['To'] = EMAIL_TO
    body = f"Jméno: {lead.name}\nEmail: {lead.email}\nIP: {lead.ip}\n\n{lead.message}"
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
        s.set_debuglevel(0)
        s.starttls()
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Simple session-based admin login. Falls back to Basic auth for API clients."""
    next_url = request.args.get('next') or request.form.get('next') or url_for('admin_leads')
    if request.method == 'GET':
        return render_template('admin_login.html', error=None, next=next_url)

    # POST: check credentials
    user = (request.form.get('username') or '').strip()
    pwd = (request.form.get('password') or '').strip()
    if user == os.environ.get('ADMIN_USER') and pwd == os.environ.get('ADMIN_PASS'):
        session['admin'] = True
        app.logger.info(f'Admin logged in from {get_client_ip()}')
        return redirect(next_url)
    app.logger.info(f'Failed admin login attempt from {get_client_ip()} user={user}')
    return render_template('admin_login.html', error='Neplatné přihlašovací údaje', next=next_url), 401


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    app.logger.info(f'Admin logged out from {get_client_ip()}')
    return redirect(url_for('home'))

@app.route('/admin/leads')
@admin_required
def admin_leads():
    s = SessionLocal()
    leads = s.query(Lead).order_by(Lead.id.desc()).limit(200).all()
    return render_template('admin_leads.html', leads=leads)

@app.route('/admin/leads/resend/<int:lead_id>', methods=['POST'])
@admin_required
def admin_resend(lead_id):
    s = SessionLocal()
    lead = s.get(Lead, lead_id)
    if not lead:
        abort(404)
    try:
        send_contact_email_from_lead(lead)
        lead.emailed = True
        lead.emailed_at = datetime.datetime.utcnow()
        lead.error = None
        s.commit()
        app.logger.info(f"Admin resent lead id={lead.id}")
    except Exception as e:
        lead.error = str(e)
        s.commit()
        app.logger.exception(f"Resend failed for lead id={lead.id}")
    return redirect(url_for('admin_leads'))

@app.route('/admin/leads/delete/<int:lead_id>', methods=['POST'])
@admin_required
def admin_delete(lead_id):
    s = SessionLocal()
    lead = s.get(Lead, lead_id)
    if not lead:
        abort(404)
    s.delete(lead)
    s.commit()
    app.logger.info(f"Admin deleted lead id={lead_id}")
    return redirect(url_for('admin_leads'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    # Use 0.0.0.0 so container/remote can reach the dev server; default port can be overridden by PORT env var
    app.run(host='0.0.0.0', port=port)