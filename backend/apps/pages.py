from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from . import page_routers as routers
from .dependencies import auth, NoAuthToken, UserSessionNotFound
from .render import FRONTEND_DIRECTORY

pages = APIRouter()

@pages.get('/')
async def root(request: Request):
    try: await auth(request)
    except (NoAuthToken, UserSessionNotFound): return RedirectResponse(url='/login', status_code=302)
    return RedirectResponse(url='/home', status_code=302)

for router in dir(routers): eval(f'pages.include_router(routers.{router}.router, prefix = \'/{router}\')') if 'router' in dir(eval(f'routers.{router}')) else None