from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from ..dependencies import auth, NoAuthToken, UserSessionNotFound
from ..render import render

router = APIRouter()

@router.get('')
async def home(request: Request):
    try: user = auth(request)
    except (NoAuthToken, UserSessionNotFound): return RedirectResponse(url='/login', status_code=302)
    return render('pages/home', {'user': user})