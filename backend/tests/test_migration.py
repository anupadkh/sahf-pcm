import json
import sqlite3
from app import database,utilities_functions

def test_existing_approved_data_and_exact_ownership_survive_migration(tmp_path,monkeypatch):
    location=tmp_path/'legacy.sqlite3'
    monkeypatch.setattr(database,'DB',location);monkeypatch.setattr(utilities_functions,'DB',location)
    monkeypatch.setenv('PCM_SEED_DEMO','false')
    with sqlite3.connect(location) as db:
        db.executescript('CREATE TABLE projects(id TEXT PRIMARY KEY,org TEXT,workflow TEXT,data TEXT,updated TEXT,review_note TEXT); CREATE TABLE audit(id INTEGER PRIMARY KEY,time TEXT,actor TEXT,action TEXT,target TEXT);')
        db.execute('INSERT INTO projects VALUES(?,?,?,?,?,?)',('legacy','Shared organization','published',json.dumps({'title':'Approved legacy record'}),'2026-09-30T10:00:00+00:00','Existing note'))
        db.execute('INSERT INTO audit(time,actor,action,target) VALUES(?,?,?,?)',('2026-09-30T10:00:00+00:00','creator@example.org','create','legacy'))
    database.initialize()
    with utilities_functions.connect() as db:
        row=db.execute('SELECT * FROM projects WHERE id=?',('legacy',)).fetchone()
        assert row['created_by']=='creator@example.org'
        assert json.loads(row['published_data'])['title']=='Approved legacy record'
        assert row['review_note']=='Existing note'
    database.initialize()
    with utilities_functions.connect() as db:assert db.execute('SELECT COUNT(*) FROM projects').fetchone()[0]==1
