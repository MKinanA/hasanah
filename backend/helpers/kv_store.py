from .db_connect import db_connect
from .sql_commands import select, insert, update, delete

class KVStore:

    @staticmethod
    async def get(key: str) -> 'str | None':
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*select('kv_store', ['value'], key=key))
            row = await cursor.fetchone()
            if row: return row['value']
            return None

    @staticmethod
    async def set(key: str, value: 'str | None') -> None:
        async with db_connect() as conn:
            cursor = await conn.cursor()
            if value is not None:
                await cursor.execute(*update('kv_store', {'key': key}, value=value))
                if cursor.rowcount <= 0: await cursor.execute(*insert('kv_store', key=key, value=value))
            else: await cursor.execute(*delete('kv_store', key=key))
            await conn.commit()