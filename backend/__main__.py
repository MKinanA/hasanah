from asyncio import run as async_run
from uvicorn import run as uvicorn_run
from .helpers.db_connect import db_connect
from .helpers.log import log
from .helpers.get_package_path import get_package_path
from .run_schema_and_seed import run_schema_and_seed
from .apps.pages import FRONTEND_DIRECTORY

print(log(__name__, f'{FRONTEND_DIRECTORY = }'))
print(log(__name__, f'{__package__ = }'))

if __name__ == "__main__":
    if not (get_package_path(__name__, __file__)/'.db').exists():
        print(log(__name__, 'Database file not found, creating...'))
        async_run(run_schema_and_seed())

    print(log(__name__, 'Testing database connection...'))
    async def init_connect():
        async with db_connect(): pass
    async_run(init_connect())

    print(log(__name__, f'Starting app {(import_string := f"{get_package_path(__name__, __file__).parts[-1]}:app")}...'))
    uvicorn_run(
        import_string,
        host='0.0.0.0',
        port=8080,
        workers=4,
    )