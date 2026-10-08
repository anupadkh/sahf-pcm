# WMO SAHF Project Coordination Mechanism

Angular frontend and FastAPI backend based on the four supplied dashboard prototypes and the v2 PCM workbook.

## Run locally

Backend (PowerShell, from this directory):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend (another terminal):

```powershell
cd frontend
npm install
npm start
```

Open http://localhost:4200. API documentation: http://127.0.0.1:8000/api/docs.
Angular 21 requires Node 20.19+, 22.12+, or compatible newer releases. The tested Node version is recorded in VALIDATION.md.

## Demo access

| Workspace | Email | Password |
| --- | --- | --- |
| Contributor | contributor@pcm.local | ChangeMe123! |
| Technical manager | reviewer@pcm.local | ChangeMe123! |
| Administrator | admin@pcm.local | ChangeMe123! |

Demo projects are illustrative records from the HTML references, not verified portfolio data. Only published records appear publicly. Contributors can access only records they personally created or uploaded. Published edits preserve the approved public version until approval. Reviewers can correct pending records, return them with a note, or publish them. Administrators can provision users, configure pillar validation, and inspect/export audit events. Tokens expire after eight hours and logout revokes them.

## Workbook integration

All 20 data columns map to the project model. Select a workbook, select the populated worksheet, then click **Import selected worksheet**. The importer prefers a populated PCM Template, then the revised portfolio sheet; it never silently imports the blank template. Worksheet discovery reports project-row counts. The original and revised portfolios are not combined. Contributors may import all supported countries; every imported record belongs to its uploader. Technical managers and administrators can import the whole selected worksheet.

Amounts such as `US$ 3.00 million` and annotated monetary amounts are converted to numeric USD; the original amount text is retained in notes. Undisclosed amounts remain null, and approximate values receive review warnings. Known-commitment totals exclude undisclosed values. Narrative text placed in the supplied workbook's Sector column is retained in notes, mapped to **Unspecified**, and marked Low confidence for technical review. Unrecognized short sector labels remain errors. Invalid flags, dates or amounts cancel the import and return row errors. Duplicate IDs are retained as drafts for moderation. Distinct external IDs may share a title, as parent projects and additional financing do in the supplied workbook. Imports create drafts rather than silently overwriting records. Download the original workbook through `/api/template`.

Legacy v1 migration is not implemented because no v1 schema/crosswalk was supplied. XLS and CSV ingestion are not implemented. Taxonomy values are maintained in `backend/app/config.py`; funding partner names accept text because the supplied portfolio contains partners absent from its reference list. No pillar alignment is allowed by default because the supplied source includes such records. IBF relevance is always a required enum on import and has an explicit default for manual forms.

## Code structure and role access

FastAPI application setup lives in `app/main.py`; URL registration in `app/routes/`; request handlers in `app/views/`; workbook parsing in `app/imports.py`; shared helpers in `app/utilities_functions.py`; authentication dependencies in `app/security.py`; models in `app/schemas.py`; and persistence initialization in `app/database.py`.

Angular bootstrap lives in `src/main.ts`. The application shell and route definitions live in `src/app/`; API/authentication services and route guards in `core/`; sign-in in `auth/`; workbook upload in `imports/`; record editing in `projects/`; dashboard views in `workspace/`; and reporting/CSV helpers in `utilities_functions/`.

Before login, navigation shows only Public overview and Sign in. Login routes each user to their own workspace. Direct access to a private route requires authentication; attempting another role's route redirects to the user's own workspace. The backend independently enforces creator ownership and role privileges. See WORKFLOW.md for published revisions, review tabs, moderation and migration.

## Deployment configuration

SQLite persists locally in `backend/pcm.sqlite3`. `PCM_DB` overrides its location; `PCM_ORIGINS` is a comma-separated allowed frontend-origin list. Set `PCM_SEED_DEMO=false` after provisioning real administrator access; changing the seed password does not modify existing accounts. Set `PCM_DEMO_PASSWORD` before the first launch to override the initial demo password. Use HTTPS, a reverse proxy forwarding `/api` to FastAPI, backups, and a managed identity provider/rate limiting before external deployment. The frontend uses relative API URLs; its development proxy is configured in `proxy.conf.json`.

Authentication uses PBKDF2 password hashing and server-stored opaque bearer sessions. This is a functional local implementation; account recovery, MFA, organization CRUD, configurable vocabulary, legacy crosswalks, geographic map boundaries, and deployment provisioning remain future work.

Build frontend: `npm run build`. Test backend: `python -m pytest` from `backend`.

After building Angular, FastAPI also serves the compiled frontend at its own origin, including the three workspace routes. For a single-server preview, open http://127.0.0.1:8000 after starting the backend. See `REPORT_MAPPING.md` for the current Power BI report mapping and `VALIDATION.md` for checks performed.

Implementation references: [Angular installation](https://angular.dev/installation), [Angular build](https://angular.dev/tools/cli/build), [FastAPI file uploads](https://fastapi.tiangolo.com/tutorial/request-files/).
