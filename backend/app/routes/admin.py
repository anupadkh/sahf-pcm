from fastapi import APIRouter
from ..views import admin as views
router = APIRouter()
router.add_api_route('/api/admin/settings', views.settings, methods=['GET'])
router.add_api_route('/api/admin/settings', views.save_settings, methods=['PUT'])
router.add_api_route('/api/admin/audit', views.logs, methods=['GET'])
router.add_api_route('/api/admin/users', views.users, methods=['GET'])
router.add_api_route('/api/admin/users', views.provision, methods=['POST'], status_code=201)

router.add_api_route('/api/admin/users/{email}', views.modify_user, methods=['PUT'])
router.add_api_route('/api/admin/users/{email}', views.delete_user, methods=['DELETE'])

router.add_api_route('/api/screen-options', views.screen_options, methods=['GET'])
router.add_api_route('/api/admin/screen-options', views.save_screen_options, methods=['PUT'])
