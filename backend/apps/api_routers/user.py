from fastapi import APIRouter, Request, Response, Depends
from ...models.user import User, Access
from ...helpers.api_response import api_response as mkresp
from ..dependencies import auth, json_body

router = APIRouter()

@router.post('')
async def user(request: Request, response: Response, user: User = Depends(auth), body: dict = Depends(json_body)) -> dict:
    try: requested_user = await User.get(username=body['username'])
    except KeyError:
        response.status_code = 400
        return mkresp('error', 'Bad Request', 'Please pass a username to look for.')
    if requested_user is None:
        response.status_code = 404
        return mkresp('error', 'Not Found', 'The requested user is not found based on the provided username.')
    return mkresp('success', 'User Found', 'User info fetched successfully.', username=requested_user.username, name=requested_user.name, **({'accesses': await requested_user.accesses} if await user.has_access(Access.ADMIN) else {}))

@router.post('/update-name')
async def update_name(request: Request, response: Response, user: User = Depends(auth), user_resp: dict = Depends(user), body: dict = Depends(json_body)):
    if user_resp['type'] != 'success': return user_resp
    target_user = await User.get(username=user_resp['username'])
    if target_user is None: raise RuntimeError('Failed to fetch user from username.')
    if not (target_user.username == user.username or user.has_access(Access.ADMIN)):
        response.status_code = 403
        return mkresp('error', 'Access Denied', 'You have no authority to update this user\'s name.')
    target_user.username = body.get('new_name') or ''
    return mkresp('success', 'Name Updated', 'User\'s name has been updated successfully.', username=target_user.username, name=target_user.name)

@router.post('/grant-access')
async def grant_access(request: Request, response: Response, user: User = Depends(auth), user_resp: dict = Depends(user), body: dict = Depends(json_body)):
    await user.require_access(Access.ADMIN)
    if (access := body['access']) == Access.ADMIN:
        response.status_code = 400
        return mkresp('error', 'Bad Request', f'Can\'t grant {access} access via API.')
    if user_resp['type'] != 'success': return user_resp
    target_user = await User.get(username=user_resp['username'])
    if target_user is None: raise RuntimeError('Failed to fetch user from username.')
    await target_user.grant_access(access)
    return mkresp('success', 'Access Granted', 'Access has been successfully granted to user.', username=target_user.username, name=target_user.name, access=access)

@router.post('/revoke-access')
async def revoke_access(request: Request, response: Response, user: User = Depends(auth), user_resp: dict = Depends(user), body: dict = Depends(json_body)):
    await user.require_access(Access.ADMIN)
    if (access := body['access']) == Access.ADMIN:
        response.status_code = 400
        return mkresp('error', 'Bad Request', f'Can\'t grant {access} access via API.')
    if user_resp['type'] != 'success': return user_resp
    target_user = await User.get(username=user_resp['username'])
    if target_user is None: raise RuntimeError('Failed to fetch user from username.')
    await target_user.revoke_access(access)
    return mkresp('success', 'Access Revoked', 'Access has been successfully revoked from user.', username=target_user.username, name=target_user.name, access=access)