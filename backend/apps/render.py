from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from ..helpers.get_package_path import get_package_path

FRONTEND_DIRECTORY = get_package_path(__name__, __file__).parent / 'frontend'

env = Environment(
    loader=FileSystemLoader(FRONTEND_DIRECTORY),
    autoescape=select_autoescape(
        enabled_extensions=('html',),
    ),
)

def render(name: str, context: 'dict | None' = None) -> HTMLResponse: return HTMLResponse(env.get_template((name + 'index.html') if name.endswith('/') else name).render(context or {}))