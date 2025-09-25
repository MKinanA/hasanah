import sqlite3 as sql
from backend import seeders
from asyncio import run
from .helpers.log import log

async def run_schema_and_seed():
    with sql.connect('.db') as conn:
        cursor = conn.cursor()
        cursor.executescript(open('schema.sql', 'r').read())
        conn.commit()

    for seeder in dir(seeders): await eval(f'{seeders.__name__}.{seeder}.seed()') if 'seed' in dir(eval(f'{seeders.__name__}.{seeder}')) else None

print(log(__name__, 'loaded')) # File load log

if __name__ == '__main__': run(run_schema_and_seed())