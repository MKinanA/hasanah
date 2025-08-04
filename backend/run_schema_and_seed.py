import sqlite3 as sql
from seeder import seed

with sql.connect('.db') as conn:
    cursor = conn.cursor()
    cursor.executescript(open('schema.sql', 'r').read())
    conn.commit()

seed()