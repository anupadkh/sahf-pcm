import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles
from .config import ROOT
from .database import initialize
from .routes import routers

initialize()
app = FastAPI(title='WMO SAHF Project Coordination Mechanism', version='1.1.0', docs_url='/api/docs', openapi_url='/api/openapi.json')
app.add_middleware(CORSMiddleware, allow_origins=os.getenv('PCM_ORIGINS','http://localhost:4200').split(','), allow_methods=['GET','POST','PUT','DELETE'], allow_headers=['Authorization','Content-Type'])
for router in routers:
    app.include_router(router)

BUILD = ROOT.parent / 'frontend' / 'dist' / 'pcm' / 'browser'
if BUILD.is_dir():
    @app.get('/', include_in_schema=False)
    @app.get('/login', include_in_schema=False)
    @app.get('/contributor', include_in_schema=False)
    @app.get('/technical-manager', include_in_schema=False)
    @app.get('/administrator/records', include_in_schema=False)
    @app.get('/administrator/users', include_in_schema=False)
    @app.get('/administrator/screen-options', include_in_schema=False)
    @app.get('/administrator/audit', include_in_schema=False)
    @app.get('/administrator', include_in_schema=False)
    def frontend():
        return FileResponse(BUILD / 'index.html')
    app.mount('/', StaticFiles(directory=BUILD), name='frontend')
