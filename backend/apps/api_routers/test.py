from fastapi import APIRouter, Request, Response
from ...models.user import User
from ...helpers.api_response import api_response as mkresp

router = APIRouter()

@router.post('/auth')
async def auth(request: Request, response: Response) -> dict:
    form = await request.form()
    token = form.get('token')

    if type(token) != str or (user := await User.get_by_session_auth(token)) is None:
        response.status_code = 401
        return mkresp('error', 'Unauthenticated', 'No token provided or token is invalid.')

    return mkresp('success', 'Authenticated', 'Token is valid.', username=user.username)