from dotenv import load_dotenv as env
from os import getenv
from ..models.user import User, JenisAkses
from ..helpers.log import log

async def seed() -> None:
    env()

    JenisAkses.add_akses('seluruhnya')

    admin = User(
        username=str(getenv('USERNAME_AKUN_ADMIN')),
        name=str(getenv('NAMA_AKUN_ADMIN')),
        password=str(getenv('PASSWORD_AKUN_ADMIN')),
    )
    await admin.save()
    await admin.grant_akses('seluruhnya')

    dummy_user = User(
        username='user',
        name='User Dummy',
        password='12345678',
    )
    await dummy_user.save()

print(log(__name__, 'loaded')) # File load log