import json
import secrets
from fastapi import Depends, HTTPException, UploadFile, Form
from ..security import current_user
from ..imports import open_workbook, discover, choose_sheet, parse_rows
from ..utilities_functions import connect, require, validate_policy, audit, now, is_duplicate

async def read_upload(file):
    if not file.filename or not file.filename.lower().endswith('.xlsx'):
        raise HTTPException(422,'Select a v2 XLSX workbook')
    content=await file.read(10*1024*1024+1)
    if len(content)>10*1024*1024:raise HTTPException(413,'Maximum upload size is 10 MB')
    return open_workbook(content)

async def sheets(file:UploadFile,user=Depends(current_user)):
    require(user,'contributor','technical_manager','administrator')
    workbook=await read_upload(file)
    try:
        available=discover(workbook)
        if not available:raise HTTPException(422,'No v2 project worksheets found')
        return {'sheets':available,'selected':choose_sheet(available)}
    finally:workbook.close()

async def import_workbook(file:UploadFile,sheet:str|None=Form(default=None),user=Depends(current_user)):
    require(user,'contributor','technical_manager','administrator')
    workbook=await read_upload(file)
    try:
        available=discover(workbook)
        selected=sheet or choose_sheet(available)
        info=next((s for s in available if s['name']==selected),None)
        if not info:raise HTTPException(422,'Select a worksheet matching the v2 template')
        parsed,errors,skipped,warnings=parse_rows(workbook[selected],user,info['header_row'])
    finally:workbook.close()
    result={'imported':0,'errors':errors,'sheet':selected,'skipped_country':skipped,'warnings':warnings}
    if not parsed and not errors:
        raise HTTPException(422,'No project rows eligible for import. Select a populated worksheet matching your organization country.')
    with connect() as db:
        existing=[json.loads(r[0]) for r in db.execute("SELECT data FROM projects WHERE workflow<>'merged'")]
        for index,project in parsed:
            try:validate_policy(db,project)
            except HTTPException as exc:
                project.import_issues+='\nEW4All pillar alignment: '+str(project.pillars)
                warnings.append({'row':index,'message':str(exc.detail)})
            if any(is_duplicate(project.model_dump(),p) for p in existing):
                warnings.append({'row':index,'message':'Potential conflict retained as a draft for reviewer/admin moderation.'})
            existing.append(project.model_dump(mode='json'))
        for _,project in parsed:
            pid=secrets.token_hex(8);stamp=now()
            db.execute('INSERT INTO projects(id,org,workflow,data,updated,created_by,created_at) VALUES(?,?,?,?,?,?,?)',(pid,user['org'],'draft',project.model_dump_json(),stamp,user['email'],stamp))
            audit(db,user,'create',pid)
        audit(db,user,'import',f'{selected}: {len(parsed)} records; {skipped} outside-country rows excluded')
    return dict(result,imported=len(parsed))

