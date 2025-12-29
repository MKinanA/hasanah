from asyncio import run as async_run
from uvicorn import run as uvicorn_run
from .helpers.db_connect import db_connect
from .helpers.log import log
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .apps.api import api
from .apps.custom_static_files import CustomStaticFiles
from .helpers.get_package_path import get_package_path
from .helpers.api_response import api_response as mkresp

FRONTEND_DIRECTORY = get_package_path(__name__, __file__).parent / 'frontend' # `../frontend/`

app = FastAPI()

@app.exception_handler(Exception)
async def exception_handler(request, exc: BaseException) -> JSONResponse: return JSONResponse(status_code=getattr(exc, 'http_status_code', 500), content=mkresp('error', type(exc).__name__, str(exc)))

app.include_router(api, prefix='/api')
app.mount('/', CustomStaticFiles(directory=FRONTEND_DIRECTORY, html=True))

print(log(__name__, f'{FRONTEND_DIRECTORY = }'))
print(log(__name__, f'{__package__ = }'))

if __name__ == "__main__":
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