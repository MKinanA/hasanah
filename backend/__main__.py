from asyncio import run as async_run
from uvicorn import run as uvicorn_run
from . import app
from .helpers.db_connect import db_connect
from .helpers.log import log

if __name__ == "__main__":
    print(log(__name__, 'Testing database connection...'))
    async def init_connect():
        async with db_connect(): pass
    async_run(init_connect())

    print(log(__name__, 'Starting app...'))
    uvicorn_run(
        app,
        host='0.0.0.0',
        port=8080,
    )