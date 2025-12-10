from dotenv import load_dotenv as env
from os import getenv
from pathlib import Path
from ..models.user import User, Access
from ..helpers.log import log

PATH = Path(__file__).parent

async def seed() -> None:
    env(PATH.parent/'.env')

    Access.add_access('seluruhnya')

    admin = User(
        username=str(getenv('USERNAME_AKUN_ADMIN')),
        name=str(getenv('NAMA_AKUN_ADMIN')),
        password=str(getenv('PASSWORD_AKUN_ADMIN')),
    )
    await admin.save()
    await admin.grant_access('seluruhnya')

    dummy_user = User(
        username='user',
        name='User Dummy',
        password='12345678',
    )
    await dummy_user.save()

print(log(__name__, 'loaded')) # File load log