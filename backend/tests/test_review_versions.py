from test_workflow import client,auth,payload,workbook_file,row
from app.utilities_functions import connect

def create(headers,title,external_id):
    body=payload();body.update(title=title,external_id=external_id)
    response=client.post('/api/projects',headers=headers,json=body)
    assert response.status_code==201,response.json()
    return response.json(),body

def submit(headers,pid):
    result=client.post(f'/api/projects/{pid}/transition',headers=headers,json={'action':'submit'})
    assert result.status_code==200,result.json()

def publish(headers,pid):
    result=client.post(f'/api/projects/{pid}/transition',headers=headers,json={'action':'publish'})
    assert result.status_code==200,result.json()

def public(pid):return next(p for p in client.get('/api/public/projects').json() if p['id']==pid)

def test_approved_record_stays_public_during_edit_return_and_resubmit():
    contributor=auth('contributor@pcm.local');reviewer=auth('reviewer@pcm.local')
    project,body=create(contributor,'Versioned flood project','VERS-001');pid=project['id']
    submit(contributor,pid);publish(reviewer,pid)
    body['title']='Revised flood project';body['commitment_usd']=250000
    updated=client.put(f'/api/projects/{pid}',headers=contributor,json=body)
    assert updated.status_code==200 and updated.json()['workflow']=='pending_review'
    assert updated.json()['has_published']
    assert public(pid)['title']=='Versioned flood project' and public(pid)['commitment_usd']==100000
    result=client.post(f'/api/projects/{pid}/transition',headers=reviewer,json={'action':'return','note':'Confirm revised funding'})
    assert result.status_code==200
    assert public(pid)['title']=='Versioned flood project'
    own=next(p for p in client.get('/api/projects',headers=contributor).json() if p['id']==pid)
    assert own['comments'][0]['comment']=='Confirm revised funding'
    body['notes']='Confirmed revised funding'
    assert client.put(f'/api/projects/{pid}',headers=contributor,json=body).json()['workflow']=='pending_review'
    publish(reviewer,pid)
    assert public(pid)['title']=='Revised flood project' and public(pid)['notes']=='Confirmed revised funding'
    with connect() as db:assert db.execute('SELECT COUNT(*) FROM project_history WHERE project_id=?',(pid,)).fetchone()[0]>=5

def test_same_organization_contributors_only_see_personal_records():
    admin=auth('admin@pcm.local');contributor=auth('contributor@pcm.local')
    result=client.post('/api/admin/users',headers=admin,json={'email':'colleague@pcm.local','name':'Colleague','password':'ColleaguePass123!','role':'contributor','org':'Nepal DHM','country':'Nepal'})
    assert result.status_code==201
    token=client.post('/api/auth/login',json={'email':'colleague@pcm.local','password':'ColleaguePass123!'}).json()['token']
    colleague={'Authorization':'Bearer '+token}
    assert client.get('/api/projects',headers=colleague).json()==[]
    project,body=create(colleague,'Colleague project','OWNER-001')
    assert not any(p['id']==project['id'] for p in client.get('/api/projects',headers=contributor).json())
    assert client.put('/api/projects/'+project['id'],headers=contributor,json=body).status_code==403
    assert any(p['id']==project['id'] and p['creator_name']=='Colleague' for p in client.get('/api/projects',headers=admin).json())

def test_conflict_requires_moderation_and_replacement_keeps_canonical_id():
    contributor=auth('contributor@pcm.local');reviewer=auth('reviewer@pcm.local')
    existing,old=create(contributor,'Original investment','CONFLICT-001');submit(contributor,existing['id']);publish(reviewer,existing['id'])
    incoming,new=create(contributor,'Incoming investment','CONFLICT-001');submit(contributor,incoming['id'])
    queue=client.get('/api/projects',headers=reviewer).json()
    assert next(p for p in queue if p['id']==incoming['id'])['conflicts'][0]['id']==existing['id']
    assert client.post('/api/projects/'+incoming['id']+'/transition',headers=reviewer,json={'action':'publish'}).status_code==409
    moderation={'existing_id':existing['id'],'action':'replace_existing','note':'Verified newer lender details'}
    assert client.post('/api/projects/'+incoming['id']+'/moderate',headers=contributor,json=moderation).status_code==403
    assert public(existing['id'])['title']=='Original investment'
    result=client.post('/api/projects/'+incoming['id']+'/moderate',headers=reviewer,json=moderation)
    assert result.status_code==200,result.json()
    assert public(existing['id'])['title']=='Incoming investment'
    assert not any(p['id']==incoming['id'] for p in client.get('/api/public/projects').json())
    source=next(p for p in client.get('/api/projects',headers=contributor).json() if p['id']==incoming['id'])
    assert source['workflow']=='merged'

def test_admin_can_correct_existing_conflict_without_copying_entire_incoming_record():
    contributor=auth('contributor@pcm.local');admin=auth('admin@pcm.local')
    existing,old=create(contributor,'Canonical project','CONFLICT-002');submit(contributor,existing['id']);publish(admin,existing['id'])
    incoming,new=create(contributor,'Alternative project title','CONFLICT-002');submit(contributor,incoming['id'])
    old['notes']='Selected corrected field from submission'
    result=client.post('/api/projects/'+incoming['id']+'/moderate',headers=admin,json={'existing_id':existing['id'],'action':'update_existing','changes':old,'note':'Keep original title and correct notes'})
    assert result.status_code==200,result.json()
    assert public(existing['id'])['title']=='Canonical project' and public(existing['id'])['notes']=='Selected corrected field from submission'

def test_imports_visible_to_uploader_and_moderators_as_drafts():
    contributor=auth('contributor@pcm.local');reviewer=auth('reviewer@pcm.local');admin=auth('admin@pcm.local')
    result=client.post('/api/import',headers=contributor,files={'file':('v2.xlsx',workbook_file([row('Personal imported project')]))})
    assert result.json()['imported']==1
    own=next(p for p in client.get('/api/projects',headers=contributor).json() if p['title']=='Personal imported project')
    assert own['created_by']=='contributor@pcm.local' and own['workflow']=='draft'
    for headers in [reviewer,admin]:assert any(p['id']==own['id'] for p in client.get('/api/projects',headers=headers).json())
    assert not any(p['id']==own['id'] for p in client.get('/api/public/projects').json())

def test_reviewer_cannot_approve_a_stale_open_record():
    contributor=auth('contributor@pcm.local');reviewer=auth('reviewer@pcm.local')
    project,body=create(contributor,'Stale approval protection','STALE-001');submit(contributor,project['id'])
    opened=next(p for p in client.get('/api/projects',headers=reviewer).json() if p['id']==project['id'])
    body['notes']='Changed since reviewer opened the page'
    client.put('/api/projects/'+project['id'],headers=contributor,json=body)
    submit(contributor,project['id'])
    result=client.post('/api/projects/'+project['id']+'/transition',headers=reviewer,json={'action':'publish','expected_updated':opened['updated']})
    assert result.status_code==409
