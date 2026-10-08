import json
import secrets
import sqlite3
from fastapi import Depends,HTTPException
from ..security import current_user
from ..config import COUNTRIES
from ..schemas import Settings,NewUser,UserUpdate,ScreenOptions
from ..utilities_functions import connect,require,password_hash,audit

def settings(user=Depends(current_user)):
    require(user, 'administrator')
    with connect() as db:
        return json.loads(db.execute('SELECT data FROM settings WHERE id=1').fetchone()[0])

def save_settings(body: Settings, user=Depends(current_user)):
    require(user, 'administrator')
    with connect() as db:
        db.execute('UPDATE settings SET data=? WHERE id=1', (body.model_dump_json(),))
        audit(db, user, 'settings_update', 'validation policy')
    return body

def logs(user=Depends(current_user)):
    require(user, 'administrator')
    with connect() as db:
        return [dict(r) for r in db.execute('SELECT * FROM audit ORDER BY id DESC LIMIT 500')]

def users(user=Depends(current_user)):
    require(user, 'administrator')
    with connect() as db:
        return [dict(r) for r in db.execute('SELECT email,name,role,org,country,active FROM users ORDER BY name,email')]

def provision(body: NewUser, user=Depends(current_user)):
    require(user, 'administrator')
    if body.country not in COUNTRIES:
        raise HTTPException(422, 'Invalid country')
    salt = secrets.token_hex(16)
    with connect() as db:
        try:
            db.execute('INSERT INTO users(email,name,role,org,country,salt,password) VALUES(?,?,?,?,?,?,?)', (body.email, body.name, body.role, body.org, body.country, salt, password_hash(body.password, salt)))
        except sqlite3.IntegrityError:
            raise HTTPException(409, 'Email already exists')
        audit(db, user, 'user_created', body.email)
    return {'email': body.email}

def modify_user(email:str,body:UserUpdate,user=Depends(current_user)):
    require(user,'administrator')
    if body.country not in COUNTRIES:raise HTTPException(422,'Invalid country')
    if email==user['email'] and (not body.active or body.role!='administrator'):raise HTTPException(409,'You cannot delete or demote your own administrator account')
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        previous=db.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
        if not previous:raise HTTPException(404,'User not found')
        db.execute('UPDATE users SET name=?,role=?,org=?,country=?,active=? WHERE email=?',(body.name,body.role,body.org,body.country,int(body.active),email))
        if body.password:
            salt=secrets.token_hex(16)
            db.execute('UPDATE users SET salt=?,password=? WHERE email=?',(salt,password_hash(body.password,salt),email))
        if body.password or previous['role']!=body.role or previous['active']!=int(body.active):db.execute('DELETE FROM sessions WHERE email=?',(email,))
        audit(db,user,'user_modified',email)
        return dict(db.execute('SELECT email,name,role,org,country,active FROM users WHERE email=?',(email,)).fetchone())

def delete_user(email:str,user=Depends(current_user)):
    require(user,'administrator')
    if email==user['email']:raise HTTPException(409,'You cannot delete your own administrator account')
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        if not db.execute('SELECT email FROM users WHERE email=?',(email,)).fetchone():raise HTTPException(404,'User not found')
        db.execute('UPDATE users SET active=0 WHERE email=?',(email,))
        db.execute('DELETE FROM sessions WHERE email=?',(email,))
        audit(db,user,'user_deleted',email)
    return {'ok':True}

def screen_options(user=Depends(current_user)):
    from ..screen_options import options
    with connect() as db:return options(db)

def save_screen_options(body:ScreenOptions,user=Depends(current_user)):
    require(user,'administrator')
    from ..screen_options import options,FIELDS
    known={key:internal for key,_,internal,_ in FIELDS}
    keys=[c.key for c in body.columns]
    if len(keys)!=len(set(keys)) or set(keys)!=set(known):raise HTTPException(422,'Provide each known column exactly once')
    if any(known[c.key] and not c.hidden_public for c in body.columns):raise HTTPException(422,'System fields must remain hidden from public')
    with connect() as db:
        db.execute('INSERT OR REPLACE INTO screen_options(id,data) VALUES(1,?)',(json.dumps([c.model_dump() for c in body.columns]),))
        audit(db,user,'screen_options_update','record columns')
        return options(db)
