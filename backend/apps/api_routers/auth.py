from fastapi import APIRouter, Request, Response, Depends
from ...models.user import User, Session
from ...helpers.api_response import api_response as mkresp
from ..dependencies import auth, json_body

router = APIRouter()

@router.post('/login')
async def login(request: Request, response: Response, body: dict = Depends(json_body)) -> dict:
    username = body.get('username')
    password = body.get('password')

    if type(username) != str:
        response.status_code = 400
        return mkresp('error', 'Permintaan Buruk', 'Username tidak valid.')
    if type(password) != str:
        response.status_code = 400
        return mkresp('error', 'Permintaan Buruk', 'Password tidak valid.')
    try: User.validate_username(username)
    except User.InvalidUsername as e:
        response.status_code = 400
        return mkresp('error', 'Permintaan Buruk', str(e))
    try: User.validate_password(password)
    except User.InvalidUsername as e:
        response.status_code = 400
        return mkresp('error', 'Permintaan Buruk', str(e))

    user = await User.get(username=username)
    if user is None or not user.verify_password(password):
        response.status_code = 401
        return mkresp('error', 'Tidak Terotorisasi', 'Username atau password salah.')

    token = await user.create_session()
    return mkresp('success', 'Sesi Dimulai', 'Login berhasil, sesi baru telah dibuat.', token=token)

@router.post('/logout')
async def logout(request: Request, response: Response, user: User = Depends(auth)) -> dict:
    token = getattr(user, 'token', None)

    if type(token) != str: raise RuntimeError('Failed to retrieve user session token from auth.')

    await Session.delete(token)
    return mkresp('success', 'Sesi Diakhiri', 'Logout berhasil, sesi telah dihapus.')