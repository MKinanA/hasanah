from asyncio import run
import aiosqlite as sql
from . import seeders
from .helpers.get_package_path import get_package_path
from .helpers.log import log

async def run_schema_and_seed():
    async with sql.connect(get_package_path(__name__, __file__)/'.db') as conn:
        cursor = await conn.cursor()
        await cursor.executescript(open(get_package_path(__name__, __file__)/'schema.sql', 'r').read())
        await conn.commit()
    print(log(__name__, 'Schema applied.'))

    for seeder in dir(seeders): await eval(f'seeders.{seeder}.seed()') if 'seed' in dir(eval(f'seeders.{seeder}')) else None
    print(log(__name__, 'Seeding completed.'))

if __name__ == '__main__': run(run_schema_and_seed())