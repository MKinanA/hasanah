from fastapi.responses import Response, HTMLResponse
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape
from ..models.user import User, Access
from ..helpers.get_package_path import get_package_path
from ..helpers.noneless import noneless

FRONTEND_DIRECTORY = get_package_path(__name__, __file__).parent / 'frontend'

env = Environment(
    loader=FileSystemLoader(FRONTEND_DIRECTORY),
    autoescape=select_autoescape(
        enabled_extensions=('html',),
    ),
)

def nav_menu_template(href, svg, text) -> dict: return {'href': href, 'svg': svg, 'text': text}

async def process_context(context: dict) -> dict:
    if 'user' in context and isinstance(user := context['user'], User): context['nav_menus'] = noneless((
        {
            **nav_menu_template(None, 'sack', 'ZIS'),
            'submenus': noneless((
                nav_menu_template(None, 'in', 'Payments'),
            ))
        } if (await user.has_access(Access.ZIS_PAYMENT_READ)) else None,
    ))
    return context

async def render(name: str, context: 'dict | None' = None, response: 'Response | None' = None) -> 'str | Response':
    context = await process_context(context or {})
    possible_names = (*(possible_name for possible_name in (
        name,
        name[:-1] if len(name) > 1 and name[-1] in ('/', '\\') else None,
        name + ('' if len(name) > 1 and name[-1] in ('/', '\\') else '\\' if len(name.split('\\')) > 1 else '/') + 'index.html',
        (name[:-1] if len(name) > 1 and name[-1] in ('/', '\\') else name) + ('' if name.endswith('.') else '.') + 'html',
    ) if possible_name is not None),)
    content = None
    error = None
    for possible_name in possible_names:
        try: content = env.get_template(possible_name).render(context)
        except TemplateNotFound as e:
            if error is None: error = e
            continue
        break
    if content is None: raise error if error is not None else RuntimeError('Failed to record error while attempting to get template file.')
    if isinstance(response, Response):
        response.media_type = 'text/html'
        return content
    else: return HTMLResponse(content)