import aiosqlite as sql
from .get_package_path import get_package_path

async def db_connect() -> sql.Connection:
    conn = await sql.connect(get_package_path(__name__, __file__)/'.db')
    conn.row_factory = sql.Row
    return conn