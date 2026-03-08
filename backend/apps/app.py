from dotenv import load_dotenv as env
from ..helpers.log import log
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from ..apps.api import api
from fastapi.staticfiles import StaticFiles
from jinja2 import TemplateNotFound
from ..helpers.get_package_path import get_package_path
from ..helpers.api_response import api_response as mkresp
from ..apps.pages import pages, FRONTEND_DIRECTORY
from ..apps.render import render
from ..apps.dependencies import auth

env(get_package_path(__name__, __file__)/'.env')

app = FastAPI()

@app.middleware('http')
async def middleware(request: Request, call_next):
    try: await auth(request)
    except: pass
    response = await call_next(request)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: BaseException) -> Response:
    if request.url.path.startswith('/api'): return JSONResponse(status_code=getattr(exc, 'status_code', 500), content=mkresp('error', type(exc).__name__, 'Couldn\'t find the template.' if isinstance(exc, TemplateNotFound) else str(exc)))
    else:
        user = None
        try: user = await auth(request)
        except: pass
        return await render('pages/error', {'code': str(getattr(exc, "status_code", 500)), 'error': type(exc).__name__ + ': ' + ('Couldn\'t find the template.' if isinstance(exc, TemplateNotFound) else str(exc)), **({'use_header': False} if user is None else {'user': user})}, status_code=getattr(exc, "status_code", 500))

@app.exception_handler(404)
async def not_found(request: Request, exc: BaseException) -> Response:
    if request.url.path.startswith('/api'): return JSONResponse(status_code=404, content=mkresp('error', 'Not Found', 'Couldn\'t find what you were looking for.'))
    else:
        user = None
        try: user = await auth(request)
        except: pass
        return await render('pages/error', {'code': '404', 'error': 'Tidak Ditemukan', **({'use_header': False} if user is None else {'user': user})}, status_code=404)

app.include_router(pages)
app.include_router(api, prefix='/api')
app.mount('/static', StaticFiles(directory=FRONTEND_DIRECTORY / 'static'))

print(log(__name__, f'FastAPI instance initialized'))