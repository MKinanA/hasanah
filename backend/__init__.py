from . import apps, models, seeders, helpers, run_schema_and_seed

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .apps.api import api
from .apps.custom_static_files import CustomStaticFiles
from .helpers.get_package_path import get_package_path
from .helpers.api_response import api_response as mkresp
from .helpers.log import log

FRONTEND_DIRECTORY = get_package_path(__name__, __file__).parent / 'frontend' # `../frontend/`

app = FastAPI()

@app.exception_handler(Exception)
async def exception_handler(request, exc: Exception) -> JSONResponse: return JSONResponse(http_status_code=getattr(exc, 'status_code', 500), content=mkresp('error', type(exc).__name__, str(exc)))

app.include_router(api, prefix='/api')
app.mount('/', CustomStaticFiles(directory=FRONTEND_DIRECTORY, html=True))

print(log(__name__, f'{FRONTEND_DIRECTORY = }'))
print(log(__name__, f'{__package__ = }'))