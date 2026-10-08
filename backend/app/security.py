import hashlib
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .utilities_functions import connect, now
bearer = HTTPBearer(auto_error=False)

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if not credentials:
        raise HTTPException(401, 'Sign in required')
    with connect() as db:
        user = db.execute('SELECT u.email,u.name,u.role,u.org,u.country FROM users u JOIN sessions s ON u.email=s.email WHERE u.active=1 AND s.token=? AND s.expires>?', (hashlib.sha256(credentials.credentials.encode()).hexdigest(), now())).fetchone()
    if not user:
        raise HTTPException(401, 'Session expired or invalid')
    return dict(user)
