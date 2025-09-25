from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .apps.api import api
from .apps.custom_static_files import CustomStaticFiles
from .helpers.log import log

FRONTENT_DIRECTORY = Path(__file__).parent.parent / 'frontend' # `../frontend/`

app = FastAPI()
app.mount('/api', api)
app.mount('/', CustomStaticFiles(directory=FRONTENT_DIRECTORY, html=True))

print(log(__name__, 'loaded')) # log