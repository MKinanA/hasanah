from fastapi import Request
from json import JSONDecodeError
from ...models.user import User

class NoAuthToken(Exception): status_code = 401
class UserSessionNotFound(Exception): status_code = 401
class InvalidBodyFormat(Exception): status_code = 400

async def auth(request: Request) -> User:
    user = await User.get_by_session_auth(token) if type(token := (await request.json()).get('token')) == str else None
    if user is None:
        if token is None: raise NoAuthToken('Please provide a session token for this request.')
        raise UserSessionNotFound('Can\'t find your session, try logging in again.')
    return user

async def json_body(request: Request) -> dict:
    try: body = await request.json()
    except JSONDecodeError as e: raise InvalidBodyFormat(f'Failed to parse request body as JSON.\n{type(e).__name__}: {str(e)}') from e
    if not isinstance(body, dict): raise InvalidBodyFormat(f'Body must be convertible to a Python dict, not {type(body).__name__}.')
    return body