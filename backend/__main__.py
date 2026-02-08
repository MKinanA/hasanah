from asyncio import run as async_run
from uvicorn import run as uvicorn_run
from .helpers.db_connect import db_connect
from .helpers.log import log
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from .apps.api import api
from fastapi.staticfiles import StaticFiles
from jinja2 import TemplateNotFound
from .helpers.get_package_path import get_package_path
from .helpers.api_response import api_response as mkresp
from .run_schema_and_seed import run_schema_and_seed
from .apps.pages import pages, FRONTEND_DIRECTORY
from .apps.render import render
from .apps.dependencies import auth

app = FastAPI()

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

print(log(__name__, f'{FRONTEND_DIRECTORY = }'))
print(log(__name__, f'{__package__ = }'))

if __name__ == "__main__":
    if not (get_package_path(__name__, __file__)/'.db').exists():
        print(log(__name__, 'Database file not found, creating...'))
        async_run(run_schema_and_seed())

    print(log(__name__, 'Testing database connection...'))
    async def init_connect():
        async with db_connect(): pass
    async_run(init_connect())

    print(log(__name__, 'Starting app...'))
    uvicorn_run(
        app,
        host='0.0.0.0',
        port=8080,
    )