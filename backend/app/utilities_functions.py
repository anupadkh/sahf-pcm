import sqlite3
import hashlib
import json
import re
from datetime import datetime, timezone
from fastapi import HTTPException
from .config import DB

def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

def now():
    return datetime.now(timezone.utc).isoformat()

def is_duplicate(project, candidate):
    """Distinct lender IDs can legitimately share a title (parent and financing)."""
    if project.get('external_id') and candidate.get('external_id'):
        return project['external_id'] == candidate['external_id']
    return project['title'].casefold() == candidate['title'].casefold() and project['country'] == candidate['country']

def password_hash(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 260000).hex()

def audit(db, user, action, target):
    db.execute('INSERT INTO audit(time,actor,action,target) VALUES(?,?,?,?)', (now(), user['email'], action, target))

def require(user, *roles):
    if user['role'] not in roles:
        raise HTTPException(403, 'Your role cannot perform this action')

def record(row):
    return dict(**json.loads(row['data']), id=row['id'], org=row['org'], workflow=row['workflow'], updated=row['updated'], review_note=row['review_note'],created_by=row['created_by'],created_at=row['created_at'])

def get_record(db, pid, user):
    row = db.execute('SELECT * FROM projects WHERE id=?', (pid,)).fetchone()
    if not row:
        raise HTTPException(404, 'Project not found')
    if user['role'] == 'contributor' and row['created_by'] != user['email']:
        raise HTTPException(403, 'You can only access records you created or uploaded')
    return row

def validate_policy(db, project):
    settings = json.loads(db.execute('SELECT data FROM settings WHERE id=1').fetchone()[0])
    if settings['enforce_pillars'] and not project.pillars:
        raise HTTPException(422, 'At least one EW4All pillar is required by current policy')

def amount(value):
    if isinstance(value, (float, int)):
        return float(value)
    text = str(value or '').lower().replace(',', '')
    match = re.fullmatch(r'\s*(?:us\$|usd|\$)?\s*(\d+(?:\.\d+)?)\s*(million|billion)?\s*', text)
    if not match:
        raise ValueError('Invalid USD amount')
    return float(match[1]) * {'million': 1e6, 'billion': 1e9, None: 1}[match[2]]

def cell_date(value):
    if isinstance(value, datetime):
        return value.date()
    return value or None
