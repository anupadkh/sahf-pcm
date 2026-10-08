from test_workflow import client,auth,payload

def test_screen_options_public_projection_and_admin_permissions():
    admin=auth('admin@pcm.local');reviewer=auth('reviewer@pcm.local');owner=auth('contributor@pcm.local')
    body={**payload(),'title':'Public column controls','external_id':'SCREEN-COLS-001','description':'Public description','notes':'Business notes'}
    record=client.post('/api/projects',headers=owner,json=body).json();pid=record['id']
    assert client.post('/api/projects/'+pid+'/transition',headers=admin,json={'action':'publish'}).status_code==200
    original=client.get('/api/screen-options',headers=admin).json()
    columns=[{k:c[k] for k in ['key','hidden_public','show_table']} for c in original]
    public=next(p for p in client.get('/api/public/projects').json() if p['id']==pid)
    assert public['description']==body['description']
    assert not {'workflow','updated','confidence','created_by','creator_name','org','review_note','import_issues'}.intersection(public)
    assert client.get('/api/screen-options').status_code==401
    assert client.put('/api/admin/screen-options',headers=reviewer,json={'columns':columns}).status_code==403
    altered=[dict(c) for c in columns]
    for c in altered:
        if c['key']=='commitment_usd':c['hidden_public']=True
        if c['key']=='description':c['show_table']=True
    try:
        result=client.put('/api/admin/screen-options',headers=admin,json={'columns':altered})
        assert result.status_code==200
        public=next(p for p in client.get('/api/public/projects').json() if p['id']==pid)
        assert 'commitment_usd' not in public and public['description']==body['description']
        private=next(p for p in client.get('/api/projects',headers=owner).json() if p['id']==pid)
        assert private['commitment_usd']==body['commitment_usd']
        options=client.get('/api/public/screen-options').json()
        assert not any(c['internal'] for c in options)
        assert next(c for c in options if c['key']=='description')['show_table']
        invalid=[dict(c) for c in altered]
        next(c for c in invalid if c['key']=='workflow')['hidden_public']=False
        assert client.put('/api/admin/screen-options',headers=admin,json={'columns':invalid}).status_code==422
        assert client.put('/api/admin/screen-options',headers=admin,json={'columns':altered[:-1]}).status_code==422
    finally:
        assert client.put('/api/admin/screen-options',headers=admin,json={'columns':columns}).status_code==200
