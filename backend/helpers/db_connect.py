from contextlib import asynccontextmanager
import aiosqlite as sql
from aiosqlite import Connection, Cursor
from .get_package_path import get_package_path

@asynccontextmanager
async def db_connect(**pragma):
    conn = await sql.connect(get_package_path(__name__, __file__)/'.db')
    conn.row_factory = sql.Row

    if not 'foreign_keys' in pragma: pragma['foreign_keys'] = 'ON'
    if not 'synchronous' in pragma: pragma['synchronous'] = 'FULL'

    for key, value in pragma.items(): await conn.execute(f'PRAGMA {key} = {value}')
    try: yield conn
    finally: await conn.close()