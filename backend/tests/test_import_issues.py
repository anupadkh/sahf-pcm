from test_workflow import client,auth,workbook_file,row,payload

def test_import_issue_values_retained_and_corrected_before_publication():
    owner=auth('contributor@pcm.local');moderator=auth('reviewer@pcm.local')
    bad=row('Multiple invalid cells','invalid amount');bad[7]='Invalid status';bad[8]='yesterday';bad[11]='Maybe';bad[17]='Invalid sector'
    result=client.post('/api/import',headers=owner,files={'file':('issues.xlsx',workbook_file([bad,row('Good alongside invalid')]))})
    assert result.status_code==200 and result.json()['imported']==2
    record=next(p for p in client.get('/api/projects',headers=owner).json() if p['title']=='Multiple invalid cells')
    for value in ['Commitment Amount (USD): invalid amount','Project Status: Invalid status','Start Date: yesterday','EW Pillar 1: Maybe','Sector: Invalid sector']:assert value in record['import_issues']
    assert record['created_by']=='contributor@pcm.local'
    assert client.post('/api/projects/'+record['id']+'/transition',headers=moderator,json={'action':'publish'}).status_code==422
    corrected=payload();corrected.update(title=record['title'],external_id=record['external_id'],import_issues='')
    assert client.put('/api/projects/'+record['id'],headers=owner,json=corrected).status_code==200
    assert client.post('/api/projects/'+record['id']+'/transition',headers=moderator,json={'action':'publish'}).status_code==200
