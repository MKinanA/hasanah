from fastapi import Request
from json import JSONDecodeError
from ..models.user import User

class NoAuthToken(Exception): status_code = 401
class DifferentAuthTokens(Exception): status_code = 400
class UserSessionNotFound(Exception): status_code = 401
class InvalidBodyFormat(Exception): status_code = 400

async def auth(request: Request) -> User:
    header_token = request.headers.get('authorization')
    header_token = (split_header_token[1] if len(split_header_token) >= 2 else split_header_token[0] if len(split_header_token) >= 1 else None) if type(header_token) == str and (split_header_token[0].lower() == 'bearer' if len(split_header_token := header_token.split()) >= 2 else True) else None
    cookie_token = request.cookies.get('token')
    json_token = (await request.json()).get('token')
    if len(set(token for token in (header_token, cookie_token, json_token) if type(token) == str)) > 1: raise DifferentAuthTokens('The provided tokens in cookies and json body are different.')
    user = (await User.get_by_session_auth(header_token)) if type(header_token) == str else (await User.get_by_session_auth(cookie_token)) if type(cookie_token) == str else (await User.get_by_session_auth(json_token)) if type(json_token) == str else None
    if user is None:
        if str not in (type(header_token), type(cookie_token), type(json_token)): raise NoAuthToken('Please provide a valid session token for this request, it could be via an `authentication` header with type `Bearer`, a `token` cookie, or a `token` field in the JSON body.')
        raise UserSessionNotFound('Can\'t find your session, try logging in again.')
    return user

async def json_body(request: Request) -> dict:
    try: body = await request.json()
    except JSONDecodeError as e: raise InvalidBodyFormat(f'Failed to parse request body as JSON.\n{type(e).__name__}: {str(e)}') from e
    if not isinstance(body, dict): raise InvalidBodyFormat(f'Body must be convertible to a Python dict, not {type(body).__name__}.')
    return body