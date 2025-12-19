from fastapi import APIRouter, Request, Response
from ...models.user import User, Session
from ...helpers.api_response import api_response as mkresp

router = APIRouter()

@router.post('/login')
async def login(request: Request, response: Response) -> dict:
    form = await request.form()
    username = form.get('username')
    password = form.get('password')

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

    token = await Session.create(user)
    return mkresp('success', 'Sesi Dimulai', 'Login berhasil, sesi baru telah dibuat.', token=token)