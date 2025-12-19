from fastapi import APIRouter
from . import api_routers as routers

api = APIRouter()
for router in dir(routers): eval(f'api.include_router(routers.{router}.router, prefix = \'/{router}\')') if 'router' in dir(eval(f'routers.{router}')) else None