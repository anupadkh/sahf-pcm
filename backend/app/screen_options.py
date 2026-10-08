"""Column registry and persisted screen options, shared by APIs and UI."""
import json
FIELDS=[
 ('title','Project / initiative',False,True),('description','Description',False,False),
 ('external_id','Project ID',False,False),('implementing_partner','Implementing partner',False,False),
 ('funding_partner','Funding partner',False,True),('country','Country',False,True),
 ('project_status','Project status',False,True),('start_date','Start date',False,False),
 ('end_date','End date',False,False),('commitment_usd','Commitment (USD)',False,True),
 ('pillars','EW4All pillars',False,False),('ibf_relevance','IBF relevance',False,False),
 ('hazard','Hazard',False,False),('sector','Sector',False,False),('multi_sector','Multi-sector',False,False),
 ('notes','Notes / remarks',False,False),('confidence','Data confidence',True,False),
 ('creator_name','Created by',True,True),('created_by','Creator email',True,False),
 ('org','Organization',True,False),('workflow','Review status',True,True),
 ('review_note','Reviewer comments',True,False),('import_issues','Issues while importing from excel',True,True),
 ('created_at','Created at',True,False),('updated','Last updated',True,False)
]

def options(db):
    stored=db.execute('SELECT data FROM screen_options WHERE id=1').fetchone()
    overrides={v['key']:v for v in json.loads(stored[0])} if stored else {}
    return [dict(key=key,label=label,internal=internal,hidden_public=internal or overrides.get(key,{}).get('hidden_public',False),show_table=overrides.get(key,{}).get('show_table',show)) for key,label,internal,show in FIELDS]

def public_record(db,row):
    fields={v['key'] for v in options(db) if not v['hidden_public'] and not v['internal']}
    return dict({k:v for k,v in json.loads(row['published_data']).items() if k in fields},id=row['id'])
