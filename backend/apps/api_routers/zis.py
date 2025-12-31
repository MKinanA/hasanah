from inspect import signature
from fastapi import APIRouter, Request, Response, Depends
from ...models.user import User, Access
from ...models.zis_payment import Payment
from ...helpers.api_response import api_response as mkresp
from .dependencies import auth, json_body

PAYMENT_QUERY_PARAMS = (*signature(Payment.query).parameters.keys(),)

router = APIRouter()

@router.post('/payments')
async def payments(request: Request, response: Response, user: User = Depends(auth), body: dict = Depends(json_body)):
    await user.require_access(Access.ZIS_PAYMENT_READ)
    payments = await Payment.query(**{key: value for key, value in body.items() if key in PAYMENT_QUERY_PARAMS})
    return mkresp('success', 'Payments Fetched', 'Successfully fetched payments.', payments=[(await (await payment.latest).to_dict) for payment in payments])

@router.post('/payment')
async def payment(request: Request, response: Response, user: User = Depends(auth), body: dict = Depends(json_body)):
    await user.require_access(Access.ZIS_PAYMENT_READ)
    uuid = body.get('uuid')
    if not isinstance(uuid, str):
        response.status_code = 400
        return mkresp('error', 'Missing or Invalid UUID', 'Please provide a valid payment UUID.')
    version = body.get('version')
    if not (version is None or isinstance(version, int)):
        try: version = int(version)
        except: pass
        if not isinstance(version, int):
            response.status_code = 400
            return mkresp('error', 'Invalid Version', 'Version parameter was provided but is invalid.')
    payment = await Payment.get(uuid=uuid)
    if payment is None:
        response.status_code = 404
        return mkresp('error', 'Payment Not Found', 'Couldn\'t fetch payment with provided UUID.')
    payment_version = await (payment.latest if version is None else payment.version(version))
    if payment_version is None:
        response.status_code = 404
        return mkresp('error', 'Payment Version Not Found', 'Couldn\'t fetch payment with provided UUID and version.')
    return mkresp('success', 'Payments Fetched', 'Successfully fetched payments.', payment=await payment_version.to_dict)