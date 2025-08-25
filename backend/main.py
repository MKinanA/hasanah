from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api import app as api
from pathlib import Path

FRONTENT_DIRECTORY = Path(__file__).parent.parent / 'frontend' # Assuming that this file is located in `backend` and the static files for frontend are in `../frontend` relative to this file

app = FastAPI()
app.mount('/api', api)
app.mount('/', StaticFiles(directory=FRONTENT_DIRECTORY, html=True))