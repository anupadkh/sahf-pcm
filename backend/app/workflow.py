import json
from .utilities_functions import is_duplicate,now

def history(db,row,user,action):
    db.execute('INSERT INTO project_history(project_id,actor,action,time,data,published_data,review_note) VALUES(?,?,?,?,?,?,?)',(row['id'],user['email'],action,now(),row['data'],row['published_data'],row['review_note']))

def conflicts(db,row):
    project=json.loads(row['data']);matches=[]
    for other in db.execute("SELECT p.*,u.name creator_name FROM projects p LEFT JOIN users u ON u.email=p.created_by WHERE p.id<>? AND p.workflow NOT IN ('merged','deleted')",(row['id'],)):
        candidate=json.loads(other['published_data'] or other['data'])
        if is_duplicate(project,candidate):
            matches.append(dict(id=other['id'],title=candidate['title'],external_id=candidate['external_id'],country=candidate['country'],workflow=other['workflow'],created_by=other['created_by'],creator_name=other['creator_name'],data=candidate,has_published=bool(other['published_data'])))
    return matches

def private_record(db,row,moderator=False):
    from .utilities_functions import record
    result=record(row)
    creator=db.execute('SELECT name FROM users WHERE email=?',(row['created_by'],)).fetchone()
    result['creator_name']=creator[0] if creator else 'Legacy creator unknown'
    result['has_published']=bool(row['published_data'])
    result['published_data']=json.loads(row['published_data']) if row['published_data'] else None
    result['conflicts']=conflicts(db,row) if moderator else []
    result['comments']=[dict(r) for r in db.execute('SELECT actor,comment,time FROM project_comments WHERE project_id=? ORDER BY id',(row['id'],))]
    result['merged_into']=row['merged_into']
    return result
