from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from ..dependencies import auth
from ..render import render

router = APIRouter()

@router.get('/')
async def register(request: Request):
    try: await auth(request)
    except: return render('register.html')
    return RedirectResponse(url='/home', status_code=302)