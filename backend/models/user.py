from __future__ import annotations
from passlib.hash import pbkdf2_sha256 as crypt
from ..helpers.db_connect import db_connect
from ..helpers.log import log
from ..helpers.sql_things import select_command as select

ALLOWED_CHARACTERS_FOR_USER_USERNAME = 'abcdefghijklmnopqrstuvwxyz0123456789_.-'
PASSWORD_HASHING_ROUNDS = 10_000

class User:
    class InvalidUsername(Exception): pass
    class InvalidName(Exception): pass
    class InvalidPassword(Exception): pass
    class InexistentUser(Exception): pass

    def __init__(self, username: str, name: str, password: str, id: int | None = None) -> None:
        self.validate_id(id)
        self.validate_username(username)
        self.validate_name(name)
        self.validate_password(password)
        self.__id = id
        self.__username = username
        self.__name = name
        self.__password = password if crypt.identify(password) else crypt.using(rounds=PASSWORD_HASHING_ROUNDS).hash(password)

    @property
    def id(self) -> int | None: return self.__id
    @id.setter
    def id(self, value: int | None) -> None:
        self.validate_id(value)
        self.__id = value

    @property
    def username(self) -> str: return self.__username
    @username.setter
    def username(self, value: str) -> None:
        self.validate_username(value)
        self.__username = value

    @property
    def name(self) -> str: return self.__name
    @name.setter
    def name(self, value: str) -> None:
        self.validate_name(value)
        self.__name = value

    @property
    def password(self) -> str: return self.__password
    def verify_password(self, password: str) -> bool: return crypt.verify(password, self.__password)
    @password.setter
    def password(self, value: str) -> None:
        self.validate_password(value)
        self.__password = value if crypt.identify(value) else crypt.using(rounds=PASSWORD_HASHING_ROUNDS).hash(value)

    def __repr__(self) -> str: return f'User(\n    id = {self.__id},\n    username = \'{self.__username}\',\n    name = \'{self.__name}\',\n    password = \'{self.__password}\'\n)'

    def validate_id(self, value) -> None:
        if not (type(value) in (int, type(None)) and (value is None or value > 0)): raise ValueError('ID harus berupa integer positif atau None.')
    def validate_username(self, value) -> None:
        if not (type(value) == str and 1 <= len(value) <= 64 and all(c in ALLOWED_CHARACTERS_FOR_USER_USERNAME for c in value)): raise self.InvalidUsername('Username harus berupa string dengan panjang 1-64 karakter dan hanya berisi huruf kecil, angka, underscore (_), titik (.), dan strip (-).')
    def validate_name(self, value) -> None:
        if not (type(value) == str and 1 <= len(value) <= 64): raise self.InvalidName('Nama harus berupa string dengan panjang 1-64 karakter.')
    def validate_password(self, value) -> None:
        if crypt.identify(value): return
        if not (type(value) == str and 8 <= len(value) <= 64): raise self.InvalidPassword('Password harus berupa string dengan panjang 8-64 karakter.')

    async def save(self) -> None:
        async with db_connect() as conn:
            cursor = await conn.cursor()
            if self.__id is None:
                await cursor.execute('INSERT INTO user (username, name, password) VALUES (?, ?, ?)', (self.__username, self.__name, self.__password))
                self.__id = cursor.lastrowid
            else: await cursor.execute('UPDATE user SET username = ?, name = ?, password = ? WHERE id = ?', (self.__username, self.__name, self.__password, self.__id))
            await conn.commit()

    @staticmethod
    async def get(**kwargs) -> User | None:
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*select(**kwargs))
            row = await cursor.fetchone()
            if row: return User(row[1], row[2], row[3], id=row[0])

    @staticmethod
    async def get_all(**kwargs) -> list[User]:
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*select(**kwargs))
            rows = await cursor.fetchall()
            return [User(row[1], row[2], row[3], id=row[0]) for row in rows]

    async def delete(self) -> None:
        if self.__id is None: return
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute('DELETE FROM user WHERE id = ?', (self.__id,))
            await conn.commit()
            self.__id = None

    @property
    async def accesses(self) -> list:
        if self.__id is None: raise self.InexistentUser('User ini tidak ada di database, mungkin belum disimpan atau sudah dihapus.')
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute('SELECT access FROM r_user_access WHERE user = ?', (self.__id,))
            return [await Access.get_name_by_id(row[0]) for row in await cursor.fetchall()]

    async def grant_access(self, access: str) -> None:
        if self.__id is None: raise self.InexistentUser('User ini tidak ada di database, mungkin belum disimpan atau sudah dihapus.')
        access_id = await Access.get_id_by_name(access)
        if access_id is None: raise Access.InvalidAccess(f'Akses "{access}" tidak valid.')
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute('SELECT COUNT(*) FROM r_user_access WHERE user = ? AND access = ?', (self.__id, access_id))
            if (fetchone := await cursor.fetchone()) and fetchone[0] > 0: return
            await cursor.execute('INSERT INTO r_user_access (user, access) VALUES (?, ?)', (self.__id, access_id))
            await conn.commit()

    async def revoke_access(self, access: str) -> None:
        if self.__id is None: raise self.InexistentUser('User ini tidak ada di database, mungkin belum disimpan atau sudah dihapus.')
        access_id = await Access.get_id_by_name(access)
        if access_id is None: raise Access.InvalidAccess(f'Akses "{access}" tidak valid.')
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute('DELETE FROM r_user_access WHERE user = ? AND access = ?', (self.__id, access_id))
            await conn.commit()

class Access:
    class InvalidAccess(Exception): pass

    @staticmethod
    async def get_name_by_id(id: int) -> str | None:
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute('SELECT name FROM access WHERE id = ?', (id,))
            row = await cursor.fetchone()
            if row: return row[0]

    @staticmethod
    async def get_id_by_name(access: str) -> int | None:
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute('SELECT id FROM access WHERE name = ?', (access.lower(),))
            row = await cursor.fetchone()
            if row: return row[0]

    @staticmethod
    async def add_access(access: str) -> None:
        if not (type(access) == str and 1 <= len(access) <= 64 and access.islower()):
            raise Access.InvalidAccess('Akses harus berupa string dengan panjang 1-64 karakter dan hanya berisi huruf kecil.')
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute('SELECT COUNT(*) FROM access WHERE name = ?', (access.lower(),))
            if (fetchone := await cursor.fetchone()) and fetchone[0] > 0: return
            await cursor.execute('INSERT INTO access (name) VALUES (?)', (access.lower(),))
            await conn.commit()