from os import environ as env
from ..models.user import User, Access
from ..helpers.log import log

async def seed() -> None:
    for name, value in vars(Access).items():
        if name.isupper() and isinstance(value, str): await Access.create(value)

    admin = User(
        username=str(env['USERNAME_AKUN_ADMIN']),
        name=str(env['NAMA_AKUN_ADMIN']),
        password=str(env['PASSWORD_AKUN_ADMIN']),
    )
    await admin.save()
    await admin.grant_access(Access.ADMIN)

    dummy_user = User(
        username='user',
        name='User Dummy',
        password='12345678',
    )
    await dummy_user.save()