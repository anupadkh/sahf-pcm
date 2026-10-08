from .auth import router as auth_router
from .projects import router as projects_router
from .admin import router as admin_router
from .public import router as public_router
from .imports import router as imports_router
routers = [auth_router, projects_router, admin_router, public_router, imports_router]
