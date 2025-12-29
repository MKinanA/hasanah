from fastapi import APIRouter, Request, Response, Depends
from json import dumps as to_json
from ...models.user import User
from ...helpers.api_response import api_response as mkresp
from .dependencies import auth, json_body

router = APIRouter()

@router.post('/auth')
async def auth(request: Request, response: Response, user: User = Depends(auth)) -> dict:
    if user is None:
        response.status_code = 401
        return mkresp('error', 'Unauthenticated', 'No token provided or token is invalid.')

    return mkresp('success', 'Authenticated', 'Token is valid.', username=user.username)

@router.post('/request-body')
async def request_body(request: Request, response: Response, body: dict = Depends(json_body)): return mkresp('success', 'Request Received', 'Request body has been parsed as JSON.', json=body, raw=(await request.body()).decode())