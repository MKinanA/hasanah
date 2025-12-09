from pathlib import Path
import sqlite3 as sql
from . import seeders
from asyncio import run
from .helpers.log import log

PATH = Path(__file__).parent

async def run_schema_and_seed():
    with sql.connect(PATH/'.db') as conn:
        cursor = conn.cursor()
        cursor.executescript(open(PATH/'schema.sql', 'r').read())
        conn.commit()

    for seeder in dir(seeders): await eval(f'seeders.{seeder}.seed()') if 'seed' in dir(eval(f'seeders.{seeder}')) else None

print(log(__name__, 'loaded')) # File load log

if __name__ == '__main__': run(run_schema_and_seed())