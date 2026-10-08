import io
import os
import tempfile
from pathlib import Path

os.environ['PCM_DB'] = str(Path(tempfile.mkdtemp()) / 'test.sqlite3')
from fastapi.testclient import TestClient
from openpyxl import Workbook
from app.main import app
from app.utilities_functions import connect, password_hash

client = TestClient(app)

def auth(email):
    response = client.post('/api/auth/login', json={'email': email, 'password': 'ChangeMe123!'})
    assert response.status_code == 200
    return {'Authorization': 'Bearer ' + response.json()['token']}

def payload(**kwargs):
    return dict(title='Test hydromet investment', country='Nepal', commitment_usd=100000, funding_partner='ADB', pillars=[2], **kwargs)

def test_workflow_and_permissions():
    contributor, reviewer = auth('contributor@pcm.local'), auth('reviewer@pcm.local')
    assert client.get('/api/projects').status_code == 401
    result = client.post('/api/projects', headers=contributor, json=payload())
    assert result.status_code == 201
    pid = result.json()['id']
    assert not any(p['id'] == pid for p in client.get('/api/public/projects').json())
    assert client.post(f'/api/projects/{pid}/transition', headers=contributor, json={'action':'submit'}).status_code == 200
    assert client.put(f'/api/projects/{pid}', headers=contributor, json=payload()).status_code == 200
    assert client.post(f'/api/projects/{pid}/transition', headers=contributor, json={'action':'submit'}).status_code == 200
    assert client.post(f'/api/projects/{pid}/transition', headers=contributor, json={'action':'publish'}).status_code == 403
    assert client.post(f'/api/projects/{pid}/transition', headers=reviewer, json={'action':'return'}).status_code == 422
    assert client.post(f'/api/projects/{pid}/transition', headers=reviewer, json={'action':'return','note':'Check amount'}).status_code == 200
    assert client.post(f'/api/projects/{pid}/transition', headers=contributor, json={'action':'submit'}).status_code == 200
    assert client.post(f'/api/projects/{pid}/transition', headers=reviewer, json={'action':'publish'}).status_code == 200
    assert any(p['id'] == pid for p in client.get('/api/public/projects').json())
    assert client.post(f'/api/projects/{pid}/transition', headers=reviewer, json={'action':'publish'}).status_code == 200
    assert client.get('/api/admin/users', headers=contributor).status_code == 403

def test_org_scope_and_logout():
    admin = auth('admin@pcm.local')
    result = client.post('/api/admin/users', headers=admin, json=dict(email='other@pcm.local',name='Other contributor',password='LongPassword123!',role='contributor',org='Other NMHS',country='Bangladesh'))
    assert result.status_code == 201
    session = client.post('/api/auth/login', json={'email':'other@pcm.local','password':'LongPassword123!'}).json()
    headers = {'Authorization':'Bearer '+session['token']}
    assert client.get('/api/projects', headers=headers).json() == []
    assert client.post('/api/projects', headers=headers, json=dict(payload(), title='Cross country contributor record')).status_code == 201
    other_pid = next(p['id'] for p in client.get('/api/projects',headers=admin).json() if p['created_by']!='other@pcm.local')
    assert client.put('/api/projects/'+other_pid, headers=headers, json=payload()).status_code == 403
    assert client.post('/api/auth/logout', headers=headers).status_code == 200
    assert client.get('/api/auth/me', headers=headers).status_code == 401

def workbook_file(rows):
    wb=Workbook();sheet=wb.active;sheet.title='PCM Template'
    sheet.append(['NO.','Project Title','Description','Project ID','Implementing Partner','Funding Partner','Country','Project Status','Start Date','End Date','Commitment Amount (USD)','EW Pillar 1','EW Pillar 2','EW Pillar 3','EW Pillar 4','IBF Relevance','Hazard Type','Sector','Multi-sector?','Notes'])
    sheet.append(['Guidance']*20)
    for row in rows:sheet.append(row)
    output=io.BytesIO();wb.save(output);return output.getvalue()

def row(title,amount='US$ 3.00 million'):
    return [1,title,'Description',title,'DHM','ADB','Nepal','Ongoing',None,None,amount,'No','Yes','No','No','Partial','Flood','DRR','No','']

def test_import_atomic_validation_and_duplicate_detection():
    headers=auth('contributor@pcm.local')
    count=len(client.get('/api/projects',headers=headers).json())
    result=client.post('/api/import',headers=headers,files={'file':('v2.xlsx',workbook_file([row('Good'),row('Bad','invalid')]))})
    assert result.status_code==200 and result.json()['imported']==2 and result.json()['warnings'][0]['row']==4
    assert len(client.get('/api/projects',headers=headers).json())==count+2
    result=client.post('/api/import',headers=headers,files={'file':('v2.xlsx',workbook_file([row('Valid import')]))})
    assert result.json()['imported']==1
    project=next(p for p in client.get('/api/projects',headers=headers).json() if p['title']=='Valid import')
    assert project['commitment_usd']==3000000 and project['pillars']==[2] and project['ibf_relevance']=='Partial'
    result=client.post('/api/import',headers=headers,files={'file':('v2.xlsx',workbook_file([row('Valid import')]))})
    assert result.json()['imported']==1 and result.json()['warnings']

def test_validation_and_settings():
    headers=auth('contributor@pcm.local');admin=auth('admin@pcm.local')
    body=payload();body['commitment_usd']=-1
    assert client.post('/api/projects',headers=headers,json=body).status_code==422
    body=payload();body['start_date']='2026-09-30';body['end_date']='2026-01-01'
    assert client.post('/api/projects',headers=headers,json=body).status_code==422
    assert client.put('/api/admin/settings',headers=admin,json={'enforce_pillars':True,'require_ibf':True}).status_code==200
    body=payload();body['pillars']=[]
    assert client.post('/api/projects',headers=headers,json=body).status_code==422
    assert client.get('/api/admin/audit',headers=admin).json()

