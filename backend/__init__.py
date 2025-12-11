from . import apps, models, seeders, helpers, run_schema_and_seed

from fastapi import FastAPI
from .apps.api import api
from .apps.custom_static_files import CustomStaticFiles
from .helpers.get_package_path import get_package_path
from .helpers.log import log

FRONTEND_DIRECTORY = get_package_path(__name__, __file__).parent / 'frontend' # `../frontend/`

app = FastAPI()
app.mount('/api', api)
app.mount('/', CustomStaticFiles(directory=FRONTEND_DIRECTORY, html=True))

print(log(__name__, 'loaded')) # File load log
print(log(__name__, f'{FRONTEND_DIRECTORY = }'))
print(log(__name__, f'{__package__ = }'))