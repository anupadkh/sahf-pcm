import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = Path(os.getenv('PCM_DB', str(ROOT / 'pcm.sqlite3')))
COUNTRIES = ['Afghanistan', 'Bangladesh', 'Bhutan', 'India', 'Maldives', 'Myanmar', 'Nepal', 'Pakistan', 'Sri Lanka', 'Multi-Country']
TAXONOMY = dict(countries=COUNTRIES, funding_partners=['ADB', 'World Bank', 'WMO', 'CREWS', 'RIMES', 'UNDP', 'FAO', 'WFP', 'UK Met Office', 'NMHS'], hazards=['Flood', 'Drought', 'Heat', 'Cyclone', 'Multi-hazard', 'N/A'], sectors=['Agriculture', 'Health', 'DRR', 'Water', 'Energy', 'Transportation', 'Multi-sector', 'Unspecified'], project_statuses=['Planned', 'Ongoing', 'Completed'], pillars=['Disaster Risk Knowledge', 'Detection, Monitoring, Analysis and Forecasting', 'Warning Dissemination and Communication', 'Preparedness and Response'])

