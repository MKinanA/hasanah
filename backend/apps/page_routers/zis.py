from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse
from ...models.user import Access
from ...models.zis_payment import Payment, PaymentCategory, PaymentUnit
from ..dependencies import auth, NoAuthToken, UserSessionNotFound
from ..render import render

router = APIRouter()

@router.get('')
async def root(): return RedirectResponse(url=f'/{__name__.split(".")[-1]}/payments', status_code=302)

@router.get('/payments')
async def payments_index(request: Request):
    try:
        user = await auth(request)
        await user.require_access(Access.ZIS_PAYMENT_READ)
    except (NoAuthToken, UserSessionNotFound): return RedirectResponse(url='/login', status_code=302)
    except Access.AccessDenied: return RedirectResponse(url='/home', status_code=302)
    return await render('pages/zis/payments', {'user': user, 'payments': [(await (await payment.latest).to_dict) for payment in await Payment.query()]}, expose='payments')

@router.get('/payments/{uuid}')
async def payment(request: Request, response: Response, uuid: str):
    try:
        user = await auth(request)
        await user.require_access(Access.ZIS_PAYMENT_READ)
    except (NoAuthToken, UserSessionNotFound): return RedirectResponse(url='/login', status_code=302)
    except Access.AccessDenied: return RedirectResponse(url='/home', status_code=302)
    payment = await Payment.get(uuid=uuid)
    if payment is None: return await render('pages/error', {'code': '404', 'error': 'Tidak Ditemukan'}, status_code=404)
    return await render('pages/zis/payments/show', {'user': user, 'payment': await (await payment.latest).to_dict}, expose='payment')

@router.get('/payments/{uuid}/edit')
async def payment_edit(request: Request, response: Response, uuid: str):
    try:
        user = await auth(request)
        await user.require_access(Access.ZIS_PAYMENT_READ, Access.ZIS_PAYMENT_WRITE)
    except (NoAuthToken, UserSessionNotFound): return RedirectResponse(url='/login', status_code=302)
    except Access.AccessDenied: return RedirectResponse(url=f'/payments/{uuid}' if user.has_access(Access.ZIS_PAYMENT_READ) else '/home', status_code=302)
    payment = await Payment.get(uuid=uuid)
    if payment is None: return await render('pages/error', {'code': '404', 'error': 'Tidak Ditemukan'}, status_code=404)
    return await render('pages/zis/payments/edit', {'user': user, 'payment': await (await payment.latest).to_dict, 'categories': (*({'value': category, 'name': category.capitalize()} for id, category in (await PaymentCategory.get_all()).items()),), 'units': (*({'value': unit, 'name': unit.capitalize()} for id, unit in (await PaymentUnit.get_all()).items()),)}, expose='payment')