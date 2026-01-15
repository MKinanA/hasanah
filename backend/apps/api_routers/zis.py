from inspect import signature
from fastapi import APIRouter, Request, Response, Depends
from ...models.user import User, Access
from ...models.zis_payment import Payment, PaymentVersion
from ...helpers.api_response import api_response as mkresp
from ..dependencies import auth, json_body

PAYMENT_QUERY_PARAMS = (*signature(Payment.query).parameters.keys(),)

router = APIRouter()

@router.post('/payments')
async def payments(request: Request, response: Response, user: User = Depends(auth), body: dict = Depends(json_body)) -> dict:
    await user.require_access(Access.ZIS_PAYMENT_READ)
    return mkresp('success', 'Payments Fetched', 'Successfully fetched payments.', payments=[(await (await payment.latest).to_dict) for payment in await Payment.query(**{key: value for key, value in body.items() if key in PAYMENT_QUERY_PARAMS})])

@router.post('/payment')
async def payment(request: Request, response: Response, user: User = Depends(auth), body: dict = Depends(json_body)) -> dict:
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

@router.post('/payment/create')
async def create_payment(request: Request, response: Response, user: User = Depends(auth), body: dict = Depends(json_body)) -> dict:
    await user.require_access(Access.ZIS_PAYMENT_WRITE)
    payment = body.get('payment')
    if not isinstance(payment, dict):
        response.status_code = 400
        return mkresp('error', 'Missing or Invalid Payment Details', 'Please provide a valid payment detail that is convertible to Python dict.')
    payment['created_by'] = user
    try: payment = await Payment.new(payment)
    except Payment.IncompleteOrInvalidPaymentDetails:
        response.status_code = 400
        return mkresp('error', 'Invalid Payment Details', 'Please provide a valid and complete payment detail.')
    except PaymentVersion.UnauthorizedCreatedBy:
        response.status_code = 403
        return mkresp('error', 'Permission Denied', 'You don\'t have the required access for this action.')
    return mkresp('success', 'Payment Created', 'Successfully created a new payment.', uuid=payment.uuid)

@router.post('/payment/update')
async def update_payment(request: Request, response: Response, user: User = Depends(auth), body: dict = Depends(json_body)) -> dict:
    await user.require_access(Access.ZIS_PAYMENT_WRITE)
    uuid = body.get('uuid')
    if not isinstance(uuid, str):
        response.status_code = 400
        return mkresp('error', 'Missing or Invalid UUID', 'Please provide a valid payment UUID.')
    payment = await Payment.get(uuid=uuid)
    if payment is None:
        response.status_code = 404
        return mkresp('error', 'Payment Not Found', 'Couldn\'t fetch payment with provided UUID.')
    new_payment = body.get('payment')
    if not isinstance(new_payment, dict):
        response.status_code = 400
        return mkresp('error', 'Missing or Invalid Payment Details', 'Please provide a valid payment detail that is convertible to Python dict.')
    new_payment['created_by'] = user
    try: await payment.update(new_payment)
    except Payment.IncompleteOrInvalidPaymentDetails:
        response.status_code = 400
        return mkresp('error', 'Invalid Payment Details', 'Please provide a valid and complete payment detail.')
    except PaymentVersion.UnauthorizedCreatedBy:
        response.status_code = 403
        return mkresp('error', 'Permission Denied', 'You don\'t have the required access for this action.')
    return mkresp('success', 'Payment Updated', 'Successfully updated payment.', uuid=payment.uuid, version=(await payment.latest).version)

@router.post('/payment/delete')
async def delete_payment(request: Request, response: Response, user: User = Depends(auth), body: dict = Depends(json_body)) -> dict:
    await user.require_access(Access.ZIS_PAYMENT_WRITE)
    uuid = body.get('uuid')
    if not isinstance(uuid, str):
        response.status_code = 400
        return mkresp('error', 'Missing or Invalid UUID', 'Please provide a valid payment UUID.')
    payment = await Payment.get(uuid=uuid)
    if payment is None:
        response.status_code = 404
        return mkresp('error', 'Payment Not Found', 'Couldn\'t fetch payment with provided UUID.')
    try: await payment.delete(by=user)
    except PaymentVersion.UnauthorizedCreatedBy:
        response.status_code = 403
        return mkresp('error', 'Permission Denied', 'You don\'t have the required access for this action.')
    if not (await payment.latest).is_deleted:
        response.status_code = 500
        return mkresp('error', 'Failed to Delete', 'Payment deletion was attempted but couldn\'t be verified.')
    return mkresp('success', 'Payment Deleted', 'Successfully deleted payment.')