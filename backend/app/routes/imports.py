from fastapi import APIRouter
from ..views import imports as views
router=APIRouter()
router.add_api_route('/api/import/sheets',views.sheets,methods=['POST'])
router.add_api_route('/api/import',views.import_workbook,methods=['POST'])
