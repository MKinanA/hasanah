from fastapi import APIRouter, Request, Response, Depends
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
    return await render('pages/users/show', {**({'user': user, 'show_admin_options': await user.has_access(Access.ADMIN)} if user is not None else {'use_header': False}), 'target_user': {'username': target_user.username, 'name': target_user.name}}, expose='target_user')

@router.get('/{username}/accesses')
async def accesses(request: Request, username: str):
    try: user = await auth(request)
    except (NoAuthToken, UserSessionNotFound): return RedirectResponse(url='/login', status_code=302)
    if not await user.has_access(Access.ADMIN): return await render('pages/error', {'code': '403', 'error': 'Akses Ditolak', 'user': user}, status_code=403)
    target_user = await User.get(username=username)
    if target_user is None: return await render('pages/error', {'code': '404', 'error': 'User Tidak Ditemukan', 'user': user}, status_code=404)
    return await render('pages/users/accesses', {'user': user, 'target_user': {'username': target_user.username, 'name': target_user.name}, 'accesses': {access: await target_user.has_access(access, allow_admin=False) for access in (await Access.get_all()).values()}, 'admin': Access.ADMIN}, expose='target_user')