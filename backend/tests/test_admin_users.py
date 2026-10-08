from test_workflow import client,auth,payload

def test_admin_user_crud_preserves_ownership_and_revokes_access():
    admin=auth('admin@pcm.local');reviewer=auth('reviewer@pcm.local')
    body={'email':'managed@pcm.local','name':'Managed Contributor','password':'ManagedPassword123!','role':'contributor','org':'Managed Org','country':'Nepal'}
    assert client.post('/api/admin/users',headers=reviewer,json=body).status_code==403
    assert client.post('/api/admin/users',headers=admin,json=body).status_code==201
    login=client.post('/api/auth/login',json={'email':body['email'],'password':body['password']}).json();owner={'Authorization':'Bearer '+login['token']}
    record=client.post('/api/projects',headers=owner,json={**payload(),'title':'Managed user project'}).json()
    edit={k:body[k] for k in ['name','role','org','country']};edit['name']='Updated Contributor'
    assert client.put('/api/admin/users/'+body['email'],headers=reviewer,json=edit).status_code==403
    assert client.put('/api/admin/users/'+body['email'],headers=admin,json=edit).status_code==200
    record_after=next(p for p in client.get('/api/projects',headers=admin).json() if p['id']==record['id'])
    assert record_after['created_by']==body['email'] and record_after['creator_name']=='Updated Contributor'
    assert client.delete('/api/admin/users/'+body['email'],headers=reviewer).status_code==403
    assert client.delete('/api/admin/users/'+body['email'],headers=admin).status_code==200
    assert client.get('/api/auth/me',headers=owner).status_code==401
    assert client.post('/api/auth/login',json={'email':body['email'],'password':body['password']}).status_code==401
    assert next(p for p in client.get('/api/projects',headers=admin).json() if p['id']==record['id'])['created_by']==body['email']
    assert not next(u for u in client.get('/api/admin/users',headers=admin).json() if u['email']==body['email'])['active']
    assert client.put('/api/admin/users/'+body['email'],headers=admin,json=edit).status_code==200
    assert client.post('/api/auth/login',json={'email':body['email'],'password':body['password']}).status_code==200
    assert client.delete('/api/admin/users/admin@pcm.local',headers=admin).status_code==409
    assert client.put('/api/admin/users/admin@pcm.local',headers=admin,json={**edit,'role':'contributor'}).status_code==409

