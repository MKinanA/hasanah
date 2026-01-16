from fastapi import APIRouter, Request, Response, Depends
from ...models.user import User
from ...helpers.api_response import api_response as mkresp
from ..dependencies import auth, json_body

router = APIRouter()

@router.post('')
async def payments(request: Request, response: Response, user: User = Depends(auth), body: dict = Depends(json_body)) -> dict:
    requested_user = await User.get(**body)
    if requested_user is None:
        response.status_code = 404
        return mkresp('error', 'Not Found', 'The requested user is not found based on the provided queries.')
    return mkresp('success', 'User Found', 'User info fetched successfully.', username=user.username, name=user.name)