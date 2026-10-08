from pathlib import Path
from test_workflow import client, auth, workbook_file, row
from app.imports import open_workbook, discover, choose_sheet, parse_rows

REFERENCE=Path(__file__).resolve().parents[1]/'assets/WMO_SAHF_PCM_Template_v2.xlsx'

def test_supplied_workbook_upload_and_sheet_selection():
    data=REFERENCE.read_bytes()
    headers=auth('reviewer@pcm.local')
    preview=client.post('/api/import/sheets',headers=headers,files={'file':('v2.xlsx',data)})
    assert preview.status_code==200
    assert preview.json()['selected']=='(Rev) ADB and WBG Proj'
    assert next(s for s in preview.json()['sheets'] if s['name']=='PCM Template')['rows']==0
    empty=client.post('/api/import',headers=headers,files={'file':('v2.xlsx',data)},data={'sheet':'PCM Template'})
    assert empty.status_code==422
    result=client.post('/api/import',headers=headers,files={'file':('v2.xlsx',data)})
    assert result.status_code==200
    assert result.json()['imported']==24, result.json()
    assert result.json()['errors']==[]
    assert result.json()['warnings']
    records=client.get('/api/projects',headers=headers).json()
    imported=next(p for p in records if p['external_id']=='42091-032')
    assert imported['workflow']=='draft'
    assert imported['commitment_usd']==86600000
    assert any(p['commitment_usd'] is None for p in records)
    assert any(p['sector']=='Unspecified' and 'Original Sector cell' in p['notes'] for p in records)

def test_contributor_country_scope_on_reference():
    workbook=open_workbook(REFERENCE.read_bytes())
    try:
        selected=choose_sheet(discover(workbook))
        records,errors,skipped,warnings=parse_rows(workbook[selected],{'role':'contributor','country':'Nepal'},1)
        assert len(records)==24 and skipped==0 and errors==[]
        assert any(p.country!='Nepal' for _,p in records)
        assert warnings
    finally:workbook.close()

def test_import_flags_whitespace_and_unknown_sector():
    r=row('Whitespace validation')
    r[11]=' No ';r[12]=' yes ';r[15]=' partial '
    data=workbook_file([r])
    headers=auth('contributor@pcm.local')
    result=client.post('/api/import',headers=headers,files={'file':('v2.xlsx',data)})
    assert result.json()['imported']==1
    records=client.get('/api/projects',headers=headers).json()
    assert next(p for p in records if p['title']=='Whitespace validation')['pillars']==[2]
    r=row('Unknown taxonomy');r[17]='Invalid'
    result=client.post('/api/import',headers=headers,files={'file':('v2.xlsx',workbook_file([r]))})
    assert result.json()['imported']==1 and result.json()['warnings']
