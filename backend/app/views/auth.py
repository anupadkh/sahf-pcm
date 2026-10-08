import hashlib
import hmac
import secrets
from datetime import datetime,timedelta,timezone
from fastapi import Depends,HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from ..security import current_user,bearer
from ..schemas import Login
from ..utilities_functions import connect,password_hash,audit,now

def login(body: Login):
    with connect() as db:
        user = db.execute('SELECT * FROM users WHERE email=?', (body.email,)).fetchone()
        if not user or not user['active'] or not hmac.compare_digest(user['password'], password_hash(body.password, user['salt'])):
            audit(db, {'email': body.email}, 'auth_failure', 'login')
            db.commit()
            raise HTTPException(401, 'Invalid email or password')
        token = secrets.token_urlsafe(40)
        db.execute('INSERT INTO sessions VALUES(?,?,?)', (hashlib.sha256(token.encode()).hexdigest(), user['email'], (datetime.now(timezone.utc) + timedelta(hours=8)).isoformat()))
        audit(db, user, 'login', 'session')
        return dict(token=token, user={k: user[k] for k in ['email', 'name', 'role', 'org', 'country']})

def me(user=Depends(current_user)):
    return user

def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer), user=Depends(current_user)):
    with connect() as db:
        db.execute('DELETE FROM sessions WHERE token=?', (hashlib.sha256(credentials.credentials.encode()).hexdigest(),))
    return {'ok': True}
