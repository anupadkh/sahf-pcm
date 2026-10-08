from test_review_versions import create,submit,publish,public
from test_workflow import client,auth,payload

def test_published_deletion_requires_moderator_and_can_be_rejected():
    owner=auth('contributor@pcm.local');reviewer=auth('reviewer@pcm.local');admin=auth('admin@pcm.local')
    record,body=create(owner,'Deletion approval project','DELETE-PUB-001');pid=record['id']
    submit(owner,pid);publish(reviewer,pid)
    requested=client.request('DELETE','/api/projects/'+pid,headers=owner,json={'note':'No longer applicable'})
    assert requested.status_code==200 and requested.json()['workflow']=='deletion_pending'
    assert public(pid)['title']==body['title']
    assert client.put('/api/projects/'+pid,headers=owner,json=body).status_code==409
    for actor in [owner]:
        assert client.post('/api/projects/'+pid+'/transition',headers=actor,json={'action':'approve_delete'}).status_code==403
    assert client.post('/api/projects/'+pid+'/transition',headers=admin,json={'action':'reject_delete'}).json()['workflow']=='published'
    assert public(pid)
    assert client.request('DELETE','/api/projects/'+pid,headers=reviewer,json={'note':'Duplicate obsolete initiative'}).status_code==200
    assert client.post('/api/projects/'+pid+'/transition',headers=admin,json={'action':'approve_delete'}).status_code==200
    assert not any(p['id']==pid for p in client.get('/api/public/projects').json())
    assert not any(p['id']==pid for p in client.get('/api/projects',headers=admin).json())
    assert client.put('/api/projects/'+pid,headers=owner,json=body).status_code==409

def test_unpublished_deletion_and_owner_scope():
    owner=auth('contributor@pcm.local');reviewer=auth('reviewer@pcm.local');admin=auth('admin@pcm.local')
    for index,actor in enumerate([owner,reviewer,admin]):
        record,_=create(owner,'Unpublished deletion '+str(index),'DELETE-DRAFT-'+str(index))
        assert client.request('DELETE','/api/projects/'+record['id'],headers=actor,json={'note':'Withdraw draft'}).json()['workflow']=='deleted'
    record,_=create(admin,'Admin private draft','DELETE-SCOPE-001')
    assert client.request('DELETE','/api/projects/'+record['id'],headers=owner,json={'note':'Unauthorized'}).status_code==403

def test_deletion_stale_protection_and_revision_restoration():
    owner=auth('contributor@pcm.local');admin=auth('admin@pcm.local')
    record,body=create(owner,'Deletion stale revision','DELETE-STALE-001');pid=record['id']
    submit(owner,pid);publish(admin,pid)
    body['notes']='Unapproved change'
    revised=client.put('/api/projects/'+pid,headers=owner,json=body).json()
    assert client.request('DELETE','/api/projects/'+pid,headers=owner,json={'note':'Remove','expected_updated':record['updated']}).status_code==409
    requested=client.request('DELETE','/api/projects/'+pid,headers=owner,json={'note':'Remove','expected_updated':revised['updated']}).json()
    assert client.post('/api/projects/'+pid+'/transition',headers=admin,json={'action':'approve_delete','expected_updated':revised['updated']}).status_code==409
    assert client.post('/api/projects/'+pid+'/transition',headers=admin,json={'action':'reject_delete','expected_updated':requested['updated']}).json()['workflow']=='pending_review'
    assert public(pid)['notes']!='Unapproved change'


def test_technical_can_approve_contributor_deletion_and_publish():
    owner=auth('contributor@pcm.local');reviewer=auth('reviewer@pcm.local')
    record,body=create(owner,'Technical deletion approval','TECH-DELETE-001');pid=record['id']
    submit(owner,pid);publish(reviewer,pid)
    requested=client.request('DELETE','/api/projects/'+pid,headers=owner,json={'note':'Contributor removal request'}).json()
    assert public(pid)
    result=client.post('/api/projects/'+pid+'/transition',headers=reviewer,json={'action':'approve_delete','expected_updated':requested['updated']})
    assert result.status_code==200 and result.json()['workflow']=='deleted'
    assert not any(p['id']==pid for p in client.get('/api/public/projects').json())


def test_technical_can_initiate_published_delete_and_reject_request():
    owner=auth('contributor@pcm.local');reviewer=auth('reviewer@pcm.local')
    record,body=create(owner,'Technical initiated removal','TECH-DELETE-002');pid=record['id']
    submit(owner,pid);publish(reviewer,pid)
    requested=client.request('DELETE','/api/projects/'+pid,headers=reviewer,json={'note':'Reviewer removal request'})
    assert requested.status_code==200 and public(pid)
    assert client.post('/api/projects/'+pid+'/transition',headers=reviewer,json={'action':'reject_delete'}).json()['workflow']=='published'
