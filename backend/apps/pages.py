from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import RedirectResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .dependencies import auth
from ..models.user import User
from ..helpers.get_package_path import get_package_path

FRONTEND_DIRECTORY = get_package_path(__name__, __file__).parent / 'frontend'

pages = APIRouter()
env = Environment(
    loader=FileSystemLoader(FRONTEND_DIRECTORY / 'pages'),
    autoescape=select_autoescape(
        enabled_extensions=('html',),
    ),
)

@pages.get('/')
def root(request: Request, response: Response, user: User = Depends(auth)): pass