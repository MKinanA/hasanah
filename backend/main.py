from fastapi import FastAPI
from pathlib import Path
from .apps.api import api
from .apps.custom_static_files import CustomStaticFiles
from .helpers.log import log

FRONTEND_DIRECTORY = Path(__file__).parent.parent / 'frontend' # `../frontend/`

app = FastAPI()
app.mount('/api', api)
app.mount('/', CustomStaticFiles(directory=FRONTEND_DIRECTORY, html=True))

print(log(__name__, 'loaded')) # File load log
print(log(__name__, f'{FRONTEND_DIRECTORY = }'))