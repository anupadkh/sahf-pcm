from fastapi import APIRouter
from ..views import auth as views
router = APIRouter()
router.add_api_route('/api/auth/login', views.login, methods=['POST'])
router.add_api_route('/api/auth/me', views.me, methods=['GET'])
router.add_api_route('/api/auth/logout', views.logout, methods=['POST'])
