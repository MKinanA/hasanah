from fastapi import APIRouter, Request, Response, Depends
from ...models.user import User
from ...helpers.api_response import api_response as mkresp
from .auth import auth

router = APIRouter()

@router.post('/auth')
async def auth(request: Request, response: Response, user: User = Depends(auth)) -> dict:
    if user is None:
        response.status_code = 401
        return mkresp('error', 'Unauthenticated', 'No token provided or token is invalid.')

    return mkresp('success', 'Authenticated', 'Token is valid.', username=user.username)