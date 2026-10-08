from fastapi import APIRouter
from ..views import projects as views
router = APIRouter()
router.add_api_route('/api/projects', views.projects, methods=['GET'])
router.add_api_route('/api/projects', views.create, methods=['POST'], status_code=201)
router.add_api_route('/api/projects/{pid}', views.update, methods=['PUT'])
router.add_api_route('/api/projects/{pid}/transition', views.transition, methods=['POST'])
router.add_api_route('/api/projects/{pid}/moderate', views.moderate, methods=['POST'])

router.add_api_route('/api/projects/{pid}', views.delete, methods=['DELETE'])
