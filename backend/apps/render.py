from fastapi.responses import Response, HTMLResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from ..helpers.get_package_path import get_package_path

FRONTEND_DIRECTORY = get_package_path(__name__, __file__).parent / 'frontend'

env = Environment(
    loader=FileSystemLoader(FRONTEND_DIRECTORY),
    autoescape=select_autoescape(
        enabled_extensions=('html',),
    ),
)

def render(name: str, context: 'dict | None' = None, response: 'Response | None' = None) -> 'str | Response':
    content = env.get_template((name + 'index.html') if name.endswith('/') else name).render(context or {})
    if isinstance(response, Response):
        response.media_type = 'text/html'
        return content
    else: return HTMLResponse()