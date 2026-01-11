from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from ...models.user import Session
from ..dependencies import auth, NoAuthToken, UserSessionNotFound
from ..render import render

router = APIRouter()

@router.get('')
async def logout(request: Request):
    try: user = await auth(request)
    except (NoAuthToken, UserSessionNotFound): return await render('pages/login')
    token = getattr(user, 'token', None)
    if type(token) != str: raise RuntimeError('Failed to retrieve user session token from auth.')
    await Session.delete(token)
    return RedirectResponse(url='/', status_code=302)