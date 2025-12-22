from time import time
from secrets import token_urlsafe as generate_token
from hashlib import sha256 as hash
from passlib.hash import pbkdf2_sha256 as crypt
from ..helpers.db_connect import db_connect
from ..helpers.log import log
from ..helpers import sql_commands as sql

ALLOWED_CHARACTERS_FOR_USER_USERNAME = 'abcdefghijklmnopqrstuvwxyz0123456789_.-'
PASSWORD_HASHING_ROUNDS = 10_000
TOKEN_NBYTES = 64
SESSION_LIFETIME = 60 * 60 * 24 * 7

class User:
    class InvalidUsername(Exception): pass
    class InvalidName(Exception): pass
    class InvalidPassword(Exception): pass
    class InexistentUser(Exception): pass

    def __init__(self, username: str, name: str, password: str, id: 'int | None' = None) -> None:
        self.validate_id(id)
        self.validate_username(username)
        self.validate_name(name)
        self.validate_password(password)
        self.__id = id
        self.__username = username
        self.__name = name
        self.__password = password if crypt.identify(password) else crypt.using(rounds=PASSWORD_HASHING_ROUNDS).hash(password)

    @property
    def id(self) -> 'int | None': return self.__id
    @id.setter
    def id(self, value: 'int | None') -> None:
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

    def __repr__(self) -> str: return f'{type(self).__name__}(\n    id = {self.__id},\n    username = \'{self.__username}\',\n    name = \'{self.__name}\',\n    password = \'{self.__password}\'\n)'

    @staticmethod
    def validate_id(value) -> None:
        if not (type(value) in (int, type(None)) and (value is None or value > 0)): raise ValueError('ID harus berupa integer positif atau None.')
    @classmethod
    def validate_username(cls, value) -> None:
        if not (type(value) == str and 1 <= len(value) <= 64 and all(c in ALLOWED_CHARACTERS_FOR_USER_USERNAME for c in value)): raise cls.InvalidUsername('Username harus berupa string dengan panjang 1-64 karakter dan hanya berisi huruf kecil, angka, underscore (_), titik (.), dan strip (-).')
    @classmethod
    def validate_name(cls, value) -> None:
        if not (type(value) == str and 1 <= len(value) <= 64): raise cls.InvalidName('Nama harus berupa string dengan panjang 1-64 karakter.')
    @classmethod
    def validate_password(cls, value) -> None:
        if crypt.identify(value): return
        if not (type(value) == str and 8 <= len(value) <= 64): raise cls.InvalidPassword('Password harus berupa string dengan panjang 8-64 karakter.')

    async def save(self) -> None:
        async with db_connect() as conn:
            cursor = await conn.cursor()
            if self.__id is None:
                await cursor.execute(*sql.insert('user', username=self.__username, name=self.__name, password=self.__password))
                self.__id = cursor.lastrowid
            else: await cursor.execute(*sql.update('user', {'id': self.__id}, username=self.__username, name=self.__name, password=self.__password))
            await conn.commit()

    @classmethod
    async def get(cls, **kwargs) -> 'User | None':
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*sql.select('user', ['id', 'username', 'name', 'password'], **kwargs))
            row = await cursor.fetchone()
            if row: return cls(row['username'], row['name'], row['password'], id=row['id'])

    @classmethod
    async def get_all(cls, **kwargs) -> 'list[User]':
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*sql.select('user', **kwargs))
            rows = await cursor.fetchall()
            return [cls(row['username'], row['name'], row['password'], id=row['id']) for row in rows]

    async def delete(self) -> None:
        if self.__id is None: return
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*sql.delete('user', id=self.__id))
            await conn.commit()
            self.__id = None

    @property
    async def accesses(self) -> list:
        if self.__id is None: raise self.InexistentUser('User ini tidak ada di database, mungkin belum disimpan atau sudah dihapus.')
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*sql.select('r_user_access', ['access'], user=self.__id))
            return [await Access.get_name_by_id(row['access']) for row in await cursor.fetchall()]

    async def grant_access(self, access: str) -> None:
        if self.__id is None: raise self.InexistentUser('User ini tidak ada di database, mungkin belum disimpan atau sudah dihapus.')
        access_id = await Access.get_id_by_name(access)
        if access_id is None: raise Access.InvalidAccess(f'Akses "{access}" tidak valid.')
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*sql.select('r_user_access', ['COUNT(*)'], user=self.__id, access=access_id))
            if (fetchone := await cursor.fetchone()) and fetchone[0] > 0: return
            await cursor.execute(*sql.insert('r_user_access', user=self.__id, access=access_id))
            await conn.commit()

    async def revoke_access(self, access: str) -> None:
        if self.__id is None: raise self.InexistentUser('User ini tidak ada di database, mungkin belum disimpan atau sudah dihapus.')
        access_id = await Access.get_id_by_name(access)
        if access_id is None: raise Access.InvalidAccess(f'Akses "{access}" tidak valid.')
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*sql.delete('r_user_access', user=self.__id, access=access_id))
            await conn.commit()

    @staticmethod
    async def get_by_session_auth(token: str) -> 'User | None': return await Session.authenticate(token)

    async def create_session(self, token_nbytes: int = TOKEN_NBYTES) -> str: return await Session.create(self, token_nbytes)

class Access:
    class InvalidAccess(Exception): pass

    @staticmethod
    async def get_all() -> 'dict[int, str]':
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*sql.select('access', ['id', 'name']))
            rows = await cursor.fetchall()
            return {row['id']: row['name'] for row in rows}

    @staticmethod
    async def get_name_by_id(id: int) -> 'str | None':
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*sql.select('access', ['name'], id=id))
            row = await cursor.fetchone()
            if row: return row['name']

    @staticmethod
    async def get_id_by_name(access: str) -> 'int | None':
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*sql.select('access', ['id'], name=access.lower()))
            row = await cursor.fetchone()
            if row: return row['id']

    @classmethod
    async def create(cls, access: str) -> None:
        if not (type(access) == str and 1 <= len(access) <= 64 and access.islower()): raise cls.InvalidAccess('Akses harus berupa string dengan panjang 1-64 karakter dan hanya berisi huruf kecil.')
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*sql.select('access', ['COUNT(*)'], name=access.lower()))
            if (fetchone := await cursor.fetchone()) and fetchone[0] > 0: return
            await cursor.execute(*sql.insert('access', name=access.lower()))
            await conn.commit()

    @staticmethod
    async def delete(access: str) -> None:
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*sql.delete('access', name=access))
            await cursor.execute(*sql.delete('access', name=access.lower()))
            await conn.commit()

class Session:

    @staticmethod
    async def authenticate(token: str) -> 'User | None':
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute('UPDATE user_session SET last_active = ? WHERE token = ? AND last_active + ? >= ? RETURNING user', (int(time()), hash(token.encode()).hexdigest(), SESSION_LIFETIME, int(time())))
            row = await cursor.fetchone()
            await conn.commit()
            if row: return await User.get(id=row['user'])
            await Session.clean_expired()

    @staticmethod
    async def create(user: User, token_nbytes: int = TOKEN_NBYTES) -> str:
        await Session.clean_expired()
        if user.id is None: raise User.InexistentUser()
        while True:
            token = generate_token(token_nbytes)
            if await Session.authenticate(token) is None: break
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*sql.insert('user_session', user=user.id, token=hash(token.encode()).hexdigest(), last_active=int(time())))
            await conn.commit()
        return token

    @staticmethod
    async def delete(token: str) -> None:
        await Session.clean_expired()
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*sql.delete('user_session', token=hash(token.encode()).hexdigest()))
            await conn.commit()

    @staticmethod
    async def clean_expired() -> None:
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute('DELETE FROM user_session WHERE last_active + ? < ?', (SESSION_LIFETIME, int(time())))
            await conn.commit()