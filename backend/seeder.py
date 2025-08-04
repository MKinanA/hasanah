from dotenv import load_dotenv as env
from os import getenv
from models import User, JenisAkses

def seed() -> None:
    env()

    JenisAkses.add_akses('seluruhnya')

    admin = User(
        username=str(getenv('USERNAME_AKUN_ADMIN')),
        nama=str(getenv('NAMA_AKUN_ADMIN')),
        password=str(getenv('PASSWORD_AKUN_ADMIN')),
    )
    _ = admin.save()
    _ = admin.grant_akses('seluruhnya')

    dummy_user = User(
        username='user',
        nama='User Dummy',
        password='12345678',
    )
    _ = dummy_user.save()