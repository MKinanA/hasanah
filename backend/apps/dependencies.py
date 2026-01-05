from fastapi import Request
from json import JSONDecodeError
from ..models.user import User

class NoAuthToken(Exception): status_code = 401
class DifferentAuthTokens(Exception): status_code = 400
class UserSessionNotFound(Exception): status_code = 401
class InvalidBodyFormat(Exception): status_code = 400

async def auth(request: Request) -> User:
    cookie_token = request.cookies.get('token')
    json_token = (await request.json()).get('token')
    if type(cookie_token) == str and type(json_token) == str and cookie_token != json_token: raise DifferentAuthTokens('The provided tokens in cookies and json body are different.')
    user = (await User.get_by_session_auth(cookie_token)) if type(cookie_token) == str else (await User.get_by_session_auth(json_token)) if type(json_token) == str else None
    if user is None:
        if str not in (type(cookie_token), type(json_token)): raise NoAuthToken('Please provide a session token for this request.')
        raise UserSessionNotFound('Can\'t find your session, try logging in again.')
    return user

async def json_body(request: Request) -> dict:
    try: body = await request.json()
    except JSONDecodeError as e: raise InvalidBodyFormat(f'Failed to parse request body as JSON.\n{type(e).__name__}: {str(e)}') from e
    if not isinstance(body, dict): raise InvalidBodyFormat(f'Body must be convertible to a Python dict, not {type(body).__name__}.')
    return body