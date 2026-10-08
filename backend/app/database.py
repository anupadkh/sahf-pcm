import os
import json
import secrets
from .config import DB
from .schemas import Project
from .utilities_functions import connect, password_hash, now

def initialize():
    DB.parent.mkdir(parents=True, exist_ok=True)
    with connect() as db:
        db.executescript('''CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY, name TEXT, role TEXT, org TEXT, country TEXT, salt TEXT, password TEXT);
        CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,email TEXT,expires TEXT);
        CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY,org TEXT,workflow TEXT,data TEXT,updated TEXT,review_note TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,time TEXT,actor TEXT,action TEXT,target TEXT);
        CREATE TABLE IF NOT EXISTS settings(id INTEGER PRIMARY KEY,data TEXT);''')
        if 'active' not in {r[1] for r in db.execute('PRAGMA table_info(users)')}:db.execute('ALTER TABLE users ADD COLUMN active INTEGER NOT NULL DEFAULT 1')
        db.execute('INSERT OR IGNORE INTO settings VALUES(1,?)', (json.dumps(dict(enforce_pillars=False, require_ibf=True)),))
        columns={r[1] for r in db.execute('PRAGMA table_info(projects)')}
        for name,kind in [('created_by','TEXT'),('created_at','TEXT'),('published_data','TEXT'),('published_updated','TEXT'),('merged_into','TEXT'),('deletion_previous_workflow','TEXT')]:
            if name not in columns:db.execute(f'ALTER TABLE projects ADD COLUMN {name} {kind}')
        db.execute('CREATE TABLE IF NOT EXISTS project_history(id INTEGER PRIMARY KEY,project_id TEXT,actor TEXT,action TEXT,time TEXT,data TEXT,published_data TEXT)')
        history_columns={r[1] for r in db.execute('PRAGMA table_info(project_history)')}
        if 'review_note' not in history_columns:db.execute('ALTER TABLE project_history ADD COLUMN review_note TEXT')
        db.execute('CREATE TABLE IF NOT EXISTS screen_options(id INTEGER PRIMARY KEY,data TEXT NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS project_comments(id INTEGER PRIMARY KEY,project_id TEXT,actor TEXT,comment TEXT,time TEXT)')
        db.execute("UPDATE projects SET published_data=data,published_updated=updated WHERE workflow='published' AND published_data IS NULL")
        db.execute('UPDATE projects SET created_at=updated WHERE created_at IS NULL')
        for row in db.execute('SELECT id,updated,org FROM projects WHERE created_by IS NULL').fetchall():
            event=db.execute("SELECT actor FROM audit WHERE action='create' AND target=? ORDER BY id LIMIT 1",(row['id'],)).fetchone()
            if event:db.execute('UPDATE projects SET created_by=? WHERE id=?',(event[0],row['id']))
            else:
                events=db.execute("SELECT DISTINCT a.actor FROM audit a JOIN users u ON u.email=a.actor WHERE a.action='import' AND u.org=? AND ABS((julianday(a.time)-julianday(?))*86400)<5",(row['org'],row['updated'])).fetchall()
                if len(events)==1:db.execute('UPDATE projects SET created_by=? WHERE id=?',(events[0][0],row['id']))
        if os.getenv('PCM_SEED_DEMO', 'true').lower() == 'true':
            for email, name, role, org, country in [('contributor@pcm.local', 'A. Sharma', 'contributor', 'Nepal DHM', 'Nepal'), ('reviewer@pcm.local', 'Technical Reviewer', 'technical_manager', 'RIMES', 'Multi-Country'), ('admin@pcm.local', 'System Administrator', 'administrator', 'WMO', 'Multi-Country')]:
                salt = secrets.token_hex(16)
                db.execute('INSERT OR IGNORE INTO users(email,name,role,org,country,salt,password) VALUES(?,?,?,?,?,?,?)', (email, name, role, org, country, salt, password_hash(os.getenv('PCM_DEMO_PASSWORD', 'ChangeMe123!'), salt)))
            if not db.execute('SELECT 1 FROM projects LIMIT 1').fetchone():
                for title, amount, workflow in [('Karnali River Basin EWS Expansion', 1250000, 'draft'), ('National Hydromet Modernization', 3400000, 'pending_review'), ('Bagmati Flood Resilience', 5100000, 'published')]:
                    p = Project(title=title, country='Nepal', commitment_usd=amount, funding_partner='World Bank', pillars=[1, 2], ibf_relevance='Yes')
                    stamp=now()
                    db.execute('INSERT INTO projects(id,org,workflow,data,updated,created_by,created_at,published_data,published_updated) VALUES(?,?,?,?,?,?,?,?,?)', (secrets.token_hex(8), 'Nepal DHM', workflow, p.model_dump_json(), stamp,'contributor@pcm.local',stamp,p.model_dump_json() if workflow=='published' else None,stamp if workflow=='published' else None))
