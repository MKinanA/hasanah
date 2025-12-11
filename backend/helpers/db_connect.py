from contextlib import asynccontextmanager
import aiosqlite as sql
from .get_package_path import get_package_path

@asynccontextmanager
async def db_connect():
    conn = await sql.connect(get_package_path(__name__, __file__)/'.db')
    conn.row_factory = sql.Row
    try: yield conn
    finally: await conn.close()