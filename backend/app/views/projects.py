import secrets
from fastapi import Depends,HTTPException
from ..security import current_user
from ..schemas import Project,Transition,Moderation,Deletion
from ..utilities_functions import connect,get_record,validate_policy,audit,now,require,is_duplicate
from ..workflow import private_record,history,conflicts

def projects(user=Depends(current_user)):
    moderator=user['role'] in ['administrator','technical_manager']
    with connect() as db:
        rows=db.execute("SELECT * FROM projects WHERE workflow<>'deleted' ORDER BY updated DESC").fetchall()
        return [private_record(db,r,moderator) for r in rows if moderator or r['created_by']==user['email']]

def create(body:Project,user=Depends(current_user)):
    with connect() as db:
        validate_policy(db,body);pid=secrets.token_hex(8);stamp=now()
        db.execute('INSERT INTO projects(id,org,workflow,data,updated,created_by,created_at) VALUES(?,?,?,?,?,?,?)',(pid,user['org'],'draft',body.model_dump_json(),stamp,user['email'],stamp))
        audit(db,user,'create',pid)
        return private_record(db,get_record(db,pid,user))

def update(pid:str,body:Project,user=Depends(current_user)):
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        row=get_record(db,pid,user)
        if row['workflow'] in ['merged','deleted','deletion_pending']:raise HTTPException(409,'Record is consolidated, deleted or awaiting deletion approval')
        validate_policy(db,body);history(db,row,user,'edit')
        workflow='pending_review' if row['published_data'] else ('draft' if row['workflow']=='pending_review' and user['role']=='contributor' else row['workflow'])
        db.execute('UPDATE projects SET data=?,workflow=?,updated=? WHERE id=?',(body.model_dump_json(),workflow,now(),pid))
        audit(db,user,'revision_submitted' if row['published_data'] else 'edit',pid)
        return private_record(db,get_record(db,pid,user),user['role']!='contributor')

def transition(pid:str,body:Transition,user=Depends(current_user)):
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        row=get_record(db,pid,user)
        if body.expected_updated and body.expected_updated!=row['updated']:raise HTTPException(409,'Record changed since you opened it. Reload before approving.')
        if body.action in ['approve_delete','reject_delete']:
            require(user,'technical_manager','administrator')
            if row['workflow']!='deletion_pending':raise HTTPException(409,'No pending deletion request')
            history(db,row,user,body.action)
            target='deleted' if body.action=='approve_delete' else (row['deletion_previous_workflow'] or 'published')
            db.execute('UPDATE projects SET workflow=?,updated=? WHERE id=?',(target,now(),pid))
            if target=='deleted':db.execute('UPDATE projects SET published_data=NULL,published_updated=NULL WHERE id=?',(pid,))
            db.execute('INSERT INTO project_comments(project_id,actor,comment,time) VALUES(?,?,?,?)',(pid,user['email'],body.note or body.action,now()))
            audit(db,user,body.action,pid)
            return private_record(db,get_record(db,pid,user),True)
        if body.action=='submit':
            if row['workflow'] not in ['draft','returned']:raise HTTPException(409,'Only drafts or returned records can be submitted')
            target='pending_review'
        else:
            require(user,'technical_manager','administrator')
            if row['workflow'] in ['merged','deleted','deletion_pending']:raise HTTPException(409,'Record is consolidated, deleted or awaiting deletion approval')
            if body.action=='return' and not body.note.strip():raise HTTPException(422,'Explain what needs correction')
            target='published' if body.action=='publish' else 'returned'
        if target=='published':validate_policy(db,Project.model_validate_json(row['data']))
        if target=='published' and Project.model_validate_json(row['data']).import_issues.strip():raise HTTPException(422,'Resolve Issues while importing from excel and clear that field before publishing')
        if target=='published' and conflicts(db,row):raise HTTPException(409,'Resolve conflicting records using moderation before publishing')
        history(db,row,user,target)
        if body.note.strip():db.execute('INSERT INTO project_comments(project_id,actor,comment,time) VALUES(?,?,?,?)',(pid,user['email'],body.note,now()))
        db.execute('UPDATE projects SET workflow=?,review_note=?,updated=? WHERE id=?',(target,body.note or row['review_note'],now(),pid))
        if target=='published':db.execute('UPDATE projects SET published_data=data,published_updated=? WHERE id=?',(now(),pid))
        audit(db,user,target,pid)
        return private_record(db,get_record(db,pid,user),user['role']!='contributor')

def moderate(pid:str,body:Moderation,user=Depends(current_user)):
    require(user,'technical_manager','administrator')
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        incoming=get_record(db,pid,user);existing=get_record(db,body.existing_id,user)
        if pid==body.existing_id or incoming['workflow']!='pending_review':raise HTTPException(409,'Select a submitted record and a different existing record')
        if not any(c['id']==body.existing_id for c in conflicts(db,incoming)):raise HTTPException(409,'Selected records do not conflict')
        if existing['workflow'] in ['pending_review','returned','merged','deleted','deletion_pending']:raise HTTPException(409,'The existing record has an unresolved revision; resolve it before consolidation')
        data=body.changes.model_dump_json() if body.action=='update_existing' and body.changes else incoming['data']
        if body.action=='update_existing' and not body.changes:raise HTTPException(422,'Provide the corrected existing record')
        validate_policy(db,Project.model_validate_json(data))
        if Project.model_validate_json(data).import_issues.strip():raise HTTPException(422,'Resolve import issues before publishing')
        import json
        for other in db.execute("SELECT * FROM projects WHERE id NOT IN (?,?) AND published_data IS NOT NULL AND workflow<>'merged'",(pid,body.existing_id)):
            if is_duplicate(json.loads(data),json.loads(other['published_data'] or other['data'])):raise HTTPException(409,'Another conflicting record must be resolved first')
        history(db,existing,user,body.action);history(db,incoming,user,'consolidated')
        for comment_id in [existing['id'],pid]:db.execute('INSERT INTO project_comments(project_id,actor,comment,time) VALUES(?,?,?,?)',(comment_id,user['email'],body.note,now()))
        db.execute("UPDATE projects SET data=?,published_data=?,published_updated=?,updated=?,workflow='published',review_note=? WHERE id=?",(data,data,now(),now(),body.note,existing['id']))
        db.execute("UPDATE projects SET workflow='merged',published_data=NULL,merged_into=?,review_note=?,updated=? WHERE id=?",(existing['id'],body.note,now(),pid))
        audit(db,user,body.action,f'{pid} -> {existing["id"]}')
        return private_record(db,get_record(db,existing['id'],user),True)

def delete(pid:str,body:Deletion,user=Depends(current_user)):
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        row=get_record(db,pid,user)
        if row['workflow'] in ['deleted','merged','deletion_pending']:raise HTTPException(409,'Record is deleted, consolidated or already awaiting deletion approval')
        if body.expected_updated and body.expected_updated!=row['updated']:raise HTTPException(409,'Record changed. Reload before deleting.')
        target='deletion_pending' if row['published_data'] else 'deleted'
        history(db,row,user,'request_delete' if row['published_data'] else 'delete')
        db.execute('UPDATE projects SET workflow=?,deletion_previous_workflow=?,updated=? WHERE id=?',(target,row['workflow'],now(),pid))
        db.execute('INSERT INTO project_comments(project_id,actor,comment,time) VALUES(?,?,?,?)',(pid,user['email'],body.note,now()))
        audit(db,user,target,pid)
        return private_record(db,get_record(db,pid,user),user['role']!='contributor')

