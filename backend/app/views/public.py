from fastapi.responses import FileResponse
from ..config import ROOT,TAXONOMY
from ..utilities_functions import connect,record

def health():
    return {'status': 'online'}

def taxonomy():
    return TAXONOMY

def public_projects():
    with connect() as db:
        from ..screen_options import public_record
        return [public_record(db,r) for r in db.execute("SELECT * FROM projects WHERE published_data IS NOT NULL AND workflow<>'merged' ORDER BY published_updated DESC")]

def public_screen_options():
    from ..screen_options import options
    with connect() as db:return [v for v in options(db) if not v['internal']]

def template():
    return FileResponse(ROOT / 'assets' / 'WMO_SAHF_PCM_Template_v2.xlsx', filename='WMO_SAHF_PCM_Template_v2.xlsx')
