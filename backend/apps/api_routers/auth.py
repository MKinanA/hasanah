from fastapi import APIRouter, Request, Response, Depends
from ...models.user import User, Session
from ...helpers.api_response import api_response as mkresp

async def auth(request: Request) -> 'User | None': return await User.get_by_session_auth(token) if type(token := (await request.form()).get('token')) == str else None

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

    token = await user.create_session()
    return mkresp('success', 'Sesi Dimulai', 'Login berhasil, sesi baru telah dibuat.', token=token)

@router.post('/logout')
async def logout(request: Request, response: Response, user: User = Depends(auth)) -> dict:
    form = await request.form()
    token = form.get('token')

    if type(token) != str:
        response.status_code = 400
        return mkresp('error', 'Permintaan Buruk', 'Token sesi tidak valid.')
    if user is None:
        response.status_code = 401
        return mkresp('error', 'Tidak Terotorisasi', 'Sesi tidak ditemukan, token mungkin sudah kedaluwarsa.')

    await Session.delete(token)
    return mkresp('success', 'Sesi Diakhiri', 'Logout berhasil, sesi telah dihapus.')