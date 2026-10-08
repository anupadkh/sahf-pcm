"""Run once with the server venv; reads password without echoing it."""
import getpass
import os
import secrets
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
os.environ.setdefault("PCM_SEED_DEMO", "false")
from app.database import initialize
from app.utilities_functions import connect, password_hash, audit
from app.config import COUNTRIES
initialize()
email = input("Admin email: ").strip()
name = input("Admin name: ").strip()
org = input("Organization: ").strip()
country = input("Country (or Multi-Country): ").strip()
password = getpass.getpass("Admin password (at least 12 characters): ")
if getpass.getpass("Confirm password: ") != password:
    raise SystemExit("Passwords do not match")
if "@" not in email or len(name) < 2 or len(org) < 2 or country not in COUNTRIES or len(password) < 12:
    raise SystemExit("Invalid account details")
with connect() as db:
    if db.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
        raise SystemExit("Email already exists; no account was changed")
    salt = secrets.token_hex(16)
    db.execute("INSERT INTO users(email,name,role,org,country,salt,password,active) VALUES(?,?,?,?,?,?,?,1)",
               (email,name,"administrator",org,country,salt,password_hash(password,salt)))
    audit(db, {"email": email}, "bootstrap_admin", email)
print("Administrator created")
