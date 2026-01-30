from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from ..render import render
from ..dependencies import auth, NoAuthToken, UserSessionNotFound
from ...models.user import User, Access

router = APIRouter()

@router.get('')
async def root(request: Request):
    try: user = await auth(request)
    except (NoAuthToken, UserSessionNotFound): return RedirectResponse(url='/login', status_code=302)
    return await render('pages/users', {'user': user, 'users': [{'username': user.username, 'name': user.name} for user in await User.get_all()]}, expose='users')

@router.get('/{username}')
async def user(request: Request, username: str):
    user = None
    try: user = await auth(request)
    except (NoAuthToken, UserSessionNotFound): pass
    target_user = await User.get(username=username)
    if target_user is None: return await render('pages/error', {'code': '404', 'error': 'User Tidak Ditemukan', **({'user': user} if user is not None else {'use_header': False})}, status_code=404)
    return await render('pages/users/show', {**({'user': user} if user is not None else {'use_header': False}), 'target_user': {'username': target_user.username, 'name': target_user.name}}, expose='target_user')