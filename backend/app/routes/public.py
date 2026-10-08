from fastapi import APIRouter
from ..views import public as views
router = APIRouter()
router.add_api_route('/api/health', views.health, methods=['GET'])
router.add_api_route('/api/taxonomy', views.taxonomy, methods=['GET'])
router.add_api_route('/api/public/projects', views.public_projects, methods=['GET'])
router.add_api_route('/api/template', views.template, methods=['GET'])

router.add_api_route('/api/public/screen-options', views.public_screen_options, methods=['GET'])
