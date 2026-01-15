from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from ...models.user import Access
from ...models.zis_payment import Payment
from ..dependencies import auth, NoAuthToken, UserSessionNotFound
from ..render import render

router = APIRouter()

@router.get('')
async def root(): return RedirectResponse(url=f'/{__name__.split(".")[-1]}/payments', status_code=302)

@router.get('/payments')
async def index(request: Request):
    try:
        user = await auth(request)
        await user.require_access(Access.ZIS_PAYMENT_READ)
    except (NoAuthToken, UserSessionNotFound): return RedirectResponse(url='/login', status_code=302)
    except Access.AccessDenied: return RedirectResponse(url='/home', status_code=302)
    return await render('pages/zis/payments', {'user': user, 'payments': [(await (await payment.latest).to_dict) for payment in await Payment.query()]})