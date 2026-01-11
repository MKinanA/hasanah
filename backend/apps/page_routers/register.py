from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from ..dependencies import auth, NoAuthToken, UserSessionNotFound
from ..render import render

router = APIRouter()

@router.get('')
async def register(request: Request):
    try: await auth(request)
    except (NoAuthToken, UserSessionNotFound): return await render('pages/register')
    return RedirectResponse(url='/home', status_code=302)