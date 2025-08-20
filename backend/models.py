from __future__ import annotations
import sqlite3 as sql
from passlib.hash import pbkdf2_sha256 as crypt

def db_connect() -> sql.Connection: return sql.connect('.db')

ALLOWED_CHARACTERS_FOR_USER_USERNAME = 'abcdefghijklmnopqrstuvwxyz0123456789_.-'
PASSWORD_HASHING_ROUNDS = 10_000

class User:
    class InvalidUsername(Exception): pass
    class InvalidName(Exception): pass
    class InvalidPassword(Exception): pass
    class InexistentUser(Exception): pass

    def __init__(self, username: str, nama: str, password: str, id: int | None = None) -> None:
        self.validate_id(id)
        self.validate_username(username)
        self.validate_nama(nama)
        self.validate_password(password)
        self.__id = id
        self.__username = username
        self.__nama = nama
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
    def nama(self) -> str: return self.__nama
    @nama.setter
    def nama(self, value: str) -> None:
        self.validate_nama(value)
        self.__nama = value
    @property
    def password(self) -> str: return self.__password
    def verify_password(self, password: str) -> bool: return crypt.verify(password, self.__password)
    @password.setter
    def password(self, value: str) -> None:
        self.validate_password(value)
        self.__password = value if crypt.identify(value) else crypt.using(rounds=PASSWORD_HASHING_ROUNDS).hash(value)

    def __repr__(self) -> str: return f'User(\n    id = {self.__id},\n    username = \'{self.__username}\',\n    nama = \'{self.__nama}\',\n    password = \'{self.__password}\'\n)'

    def validate_id(self, value) -> None:
        if not (type(value) in (int, type(None)) and (value is None or value > 0)): raise ValueError('ID harus berupa integer positif atau None.')
    def validate_username(self, value) -> None:
        if not (type(value) == str and 1 <= len(value) <= 64 and all(c in ALLOWED_CHARACTERS_FOR_USER_USERNAME for c in value)): raise self.InvalidUsername('Username harus berupa string dengan panjang 1-64 karakter dan hanya berisi huruf kecil, angka, underscore (_), titik (.), dan strip (-).')
    def validate_nama(self, value) -> None:
        if not (type(value) == str and 1 <= len(value) <= 64): raise self.InvalidName('Nama harus berupa string dengan panjang 1-64 karakter.')
    def validate_password(self, value) -> None:
        if crypt.identify(value): return
        if not (type(value) == str and 8 <= len(value) <= 64): raise self.InvalidPassword('Password harus berupa string dengan panjang 8-64 karakter.')

    async def save(self) -> None:
        with db_connect() as conn:
            cursor = conn.cursor()
            if self.__id is None:
                cursor.execute('INSERT INTO user (username, nama, password) VALUES (?, ?, ?)', (self.__username, self.__nama, self.__password))
                self.__id = cursor.lastrowid
            else: cursor.execute('UPDATE user SET username = ?, nama = ?, password = ? WHERE id = ?', (self.__username, self.__nama, self.__password, self.__id))
            conn.commit()

    @staticmethod
    async def get_by_id(id: int) -> User | None:
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user WHERE id = ?', (id,))
            row = cursor.fetchone()
            if row: return User(row[1], row[2], row[3], id=row[0])

    @staticmethod
    async def get_all() -> list[User]:
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user')
            rows = cursor.fetchall()
            return [User(row[1], row[2], row[3], id=row[0]) for row in rows]

    @staticmethod
    async def get_by_username(username: str) -> User | None:
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user WHERE username = ?', (username,))
            row = cursor.fetchone()
            if row: return User(row[1], row[2], row[3], id=row[0])

    async def delete(self) -> None:
        if self.__id is None: return
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM user WHERE id = ?', (self.__id,))
            conn.commit()
            self.__id = None

    @property
    async def akses(self) -> list:
        if self.__id is None: raise self.InexistentUser('User ini tidak ada di database, mungkin belum disimpan atau sudah dihapus.')
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT akses FROM r_akses_user WHERE user = ?', (self.__id,))
            return [JenisAkses.get_akses_by_id(row[0]) for row in cursor.fetchall()]

    async def grant_akses(self, akses: str) -> None:
        if self.__id is None: raise self.InexistentUser('User ini tidak ada di database, mungkin belum disimpan atau sudah dihapus.')
        id_akses = JenisAkses.get_id_by_akses(akses)
        if id_akses is None: raise JenisAkses.InvalidAccess(f'Akses "{akses}" tidak valid.')
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM r_akses_user WHERE user = ? AND akses = ?', (self.__id, id_akses))
            if cursor.fetchone()[0] > 0: return
            cursor.execute('INSERT INTO r_akses_user (user, akses) VALUES (?, ?)', (self.__id, id_akses))
            conn.commit()

    async def revoke_akses(self, akses: str) -> None:
        if self.__id is None: raise self.InexistentUser('User ini tidak ada di database, mungkin belum disimpan atau sudah dihapus.')
        id_akses = JenisAkses.get_id_by_akses(akses)
        if id_akses is None: raise JenisAkses.InvalidAccess(f'Akses "{akses}" tidak valid.')
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM r_akses_user WHERE user = ? AND akses = ?', (self.__id, id_akses))
            conn.commit()

class JenisAkses:
    class InvalidAccess(Exception): pass

    @staticmethod
    def get_akses_by_id(id: int) -> str | None:
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT akses FROM jenis_akses WHERE id = ?', (id,))
            row = cursor.fetchone()
            if row: return row[0]

    @staticmethod
    def get_id_by_akses(akses: str) -> int | None:
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM jenis_akses WHERE akses = ?', (akses.lower(),))
            row = cursor.fetchone()
            if row: return row[0]

    @staticmethod
    def add_akses(akses: str) -> None:
        if not (type(akses) == str and 1 <= len(akses) <= 64 and akses.islower()):
            raise JenisAkses.InvalidAccess('Akses harus berupa string dengan panjang 1-64 karakter dan hanya berisi huruf kecil.')
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM jenis_akses WHERE akses = ?', (akses.lower(),))
            if cursor.fetchone()[0] > 0: return
            cursor.execute('INSERT INTO jenis_akses (akses) VALUES (?)', (akses.lower(),))
            conn.commit()

class ZIS:
    class InvalidAmount(Exception): pass
    class InvalidDate(Exception): pass
    class InvalidType(Exception): pass
    class InvalidNama(Exception): pass
    class InvalidNumber(Exception): pass

    class Pemasukan: pass

with db_connect() as conn: pass