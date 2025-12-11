from __future__ import annotations
from typing import Union
from dotenv import load_dotenv as env
from asyncio import Lock
from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse as Redirect, JSONResponse as JSON
from starlette.middleware.base import RequestResponseEndpoint
from starlette.exceptions import HTTPException
from backend.models.user import User
from time import time
from secrets import token_hex as generate_token
from ..helpers.log import log

# {} Exception Classes Declaration

class RequiredDataIncompleteOrInvalid(Exception): pass
class TokenNotFound(Exception): pass
class UsernameOrPasswordIncorrect(Exception): pass
class AccessDenied(Exception): pass
class PathInexists(Exception): pass
class MethodNotAllowed(Exception): pass

# {} Const Declarations

ROUTE_PREFIX = 'api'
LOGIN_SESSIONS_TEMPLATE = {
    'username': str,
    'login_time': float,
    'last_activity': float,
    'tokens': [
        str,
        Union[str, None]
    ],
}
SESSION_EXPIRES_AFTER = 60 * 60 * 24 * 7
NO_AUTH_PATHS = [
    f'{ROUTE_PREFIX}/',
    f'{ROUTE_PREFIX}/login',
    f'{ROUTE_PREFIX}/test'
]
EXCEPTION_STATUS_CODES = {
    RequiredDataIncompleteOrInvalid: {
        'code': 400,
        'meaning': 'Permintaan Buruk',
        'message': 'Data yang anda kirim tidak lengkap atau dalam bentuk yang salah untuk permintaan ini.'
    },
    TokenNotFound: {
        'code': 401,
        'meaning': 'Tidak Terotorisasi',
        'message': 'Anda tidak terotorisasi untuk permintaan ini, mungkin anda belum login atau tidak memiliki akses yang dibutuhkan.'
    },
    UsernameOrPasswordIncorrect: {
        'code': 401,
        'meaning': 'Tidak Terotorisasi',
        'message': 'Akun tidak ditemukan, mungkin username atau password yang anda kirimkan salah.'
    },
    AccessDenied: {
        'code': 403,
        'meaning': 'Akses Ditolak',
        'message': 'Anda tidak memiliki akses untuk permintaan ini.'
    },
    PathInexists: {
        'code': 404,
        'meaning': 'Tidak Ditemukan',
        'message': 'Path yang anda minta tidak ada.'
    },
    MethodNotAllowed: {
        'code': 405,
        'meaning': 'Metode Tidak Diperbolehkan',
        'message': 'Aplikasi ini hanya menerima metode HTTP "POST".'
    },
    Exception: {
        'code': 500,
        'meaning': 'Kesalahan Server Internal',
        'message': 'Terjadi kesalahan (error) di server.'
    }
}
HTTPEXCEPTION_TO_NORMAL_EXCEPTION = {
    404: PathInexists
}

# {} Preparations

env()
api = FastAPI()
login_sessions = []
login_sessions_lock = Lock()

# {} Reusable Functions

async def new_session(username: str) -> str:
    new_token = generate_token(32)
    async with login_sessions_lock:
        login_sessions.append({
            'username': username,
            'login_time': time(),
            'last_activity': time(),
            'tokens': [
                new_token,
                None
            ],
        })
    return new_token

async def authenticate(token: str) -> 'tuple[User, str]':
    user = None
    new_token = None
    index = 0
    async with login_sessions_lock:
        for session in login_sessions:
            if token in session['tokens']:
                if session['last_activity'] + SESSION_EXPIRES_AFTER < time():
                    del login_sessions[index]
                    continue
                if session['tokens'][0] == token:
                    login_sessions[index]['tokens'][1] = session['tokens'][0]
                    login_sessions[index]['tokens'][0] = new_token = generate_token(32)
                else: new_token = session['tokens'][0]
                login_sessions[index]['last_activity'] = time()
                user = await User.get(username=session['username'])
                break
            index += 1
    if type(user) != User or type(new_token) != str: raise TokenNotFound('Sesi tidak ditemukan atau sudah kadaluarsa, silahkan login dan dapatkan token baru.')
    return user, new_token

async def end_session(token: str) -> None:
    index = 0
    async with login_sessions_lock:
        for session in login_sessions:
            if token in session['tokens']:
                del login_sessions[index]
                break
            index += 1

def as_user_and_token(authentication) -> 'tuple[User, str]':
    print(authentication)
    if type(authentication) != tuple or len(authentication) != 2 or type(authentication[0]) != User or type(authentication[1]) != str: raise TypeError(f'Invalid type for authentication, {type(authentication)} != tuple[User, str]')
    return authentication

# {} Exception & Error Handlers

@api.exception_handler(Exception)
async def exception_handler(request: Request, exception: Exception) -> Response:
    response = {
        'type': 'error',
    }
    exception_found = False
    token = None
    try: _, token = as_user_and_token(request.state.authentication)
    except: pass
    for exception_class, exception_type in EXCEPTION_STATUS_CODES.items():
        if (type(exception) == exception_class or issubclass(type(exception), exception_class)) if type(exception_class) not in (list, tuple, set) else (exception in exception_class or any(issubclass(type(exception), an_exception_class) for an_exception_class in exception_class)):
            response['error'] = exception_type['meaning']
            response['message'] = str(exception) or exception_type['message']
            exception_found = True
            break
    if not exception_found:
        response['error'] = 'Tidak Diketahui'
        response['message'] = 'Terjadi kesalahan yang tidak dikenali oleh server'
    if token: response['token'] = token
    return JSON(status_code=exception_type['code'] if exception_found else 500, content=response)

@api.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exception: HTTPException) -> None: raise HTTPEXCEPTION_TO_NORMAL_EXCEPTION[exception.status_code] if exception.status_code in HTTPEXCEPTION_TO_NORMAL_EXCEPTION.keys() else Exception(f'Terjadi kesalahan {exception.status_code} dari permintaan yang tidak bisa ditangani oleh server.')

# {} Middleware (HTTP)

@api.middleware('http')
async def middleware(request: Request, handler: RequestResponseEndpoint) -> Response:
    if request.method.lower() == 'post':
        if request.url.path.strip('/') not in NO_AUTH_PATHS:
            form = await request.form()
            token = form.get('token')
            if not (type(token) == str): raise RequiredDataIncompleteOrInvalid()
            request.state.authentication = await authenticate(token)
    else: raise MethodNotAllowed()
    response = await handler(request)
    return response

# {} Route Handlers

@api.post('/login')
async def login(request: Request, response: Response):
    form = await request.form()
    username = form.get('username')
    password = form.get('password')
    if not (username and password and type(username) == str and type(password) == str and 1 <= len(username) <= 64 and 8 <= len(password) <= 64):
        response.status_code = 400
        return {
            'type': 'error',
            'error': 'Permintaan Buruk',
            'message': 'Data yang dikirimkan tidak sesuai.'
        }
    user = await User.get(username=username)
    if type(user) != User or not user.verify_password(password):
        response.status_code = 401
        return {
            'type': 'error',
            'error': 'Tidak Terotorisasi',
            'message': 'Username atau password salah, atau akun tidak tidak ada.'
        }
    new_token = await new_session(user.username)
    return {
        'type': 'success',
        'success': 'Sesi Dimulai',
        'message': 'Sesi berhasil dimulai.',
        'token': new_token
    }

@api.post('/logout')
async def logout(request: Request, response: Response):
    await end_session(as_user_and_token(request.state.authentication)[1])
    return {
        'type': 'success',
        'success': 'Sesi Diakhiri',
        'message': 'Sesi berhasil diakhiri.'
    }

# {} Test (# TODO: delete these tests)

@api.post('/do-something-as-authenticated-user')
async def do_something_as_authenticated_user(request: Request, response: Response):
    user, new_token = as_user_and_token(request.state.authentication)
    return {
        'type': 'success',
        'success': 'Did Something',
        'message': f'You did something as {user.name}. Now get your new token.',
        'token': new_token
    }