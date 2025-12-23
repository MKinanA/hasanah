from ..helpers.db_connect import db_connect, Cursor
from ..helpers.log import log
from ..helpers import sql_commands as sql

class Payment:
    class PaymentNotFound(Exception): http_status_code = 404

    def __init__(self): pass

class PaymentLine:
    class InvalidPaymentVersion(Exception): http_status_code = 400
    class InexistentPaymentVersion(Exception): http_status_code = 404
    class InvalidPayerName(Exception): http_status_code = 400
    class InvalidCategory(Exception): http_status_code = 400
    class InexistentCategory(Exception): http_status_code = 404
    class InvalidAmount(Exception): http_status_code = 400
    class InvalidNote(Exception): http_status_code = 400

    def __init__(self, payment_version: int, payer_name: str, category: str, amount: 'float | int', note: 'str | None' = None, id: 'int | None' = None):
        self.validate_id(id)
        self.validate_payment_version(payment_version)
        self.validate_payer_name(payer_name)
        self.validate_category(category)
        self.validate_amount(amount)
        self.validate_note(note)
        self.__id = id
        self.__payment_version = payment_version
        self.__payer_name = payer_name
        self.__category = category
        self.__amount = float(amount)
        self.__note = note

    @property
    def id(self) -> 'int | None': return self.__id
    @property
    def payment_version(self) -> int: return self.__payment_version
    @property
    def payer_name(self) -> str: return self.__payer_name
    @property
    def category(self) -> str: return self.__category
    @property
    def amount(self) -> float: return self.__amount
    @property
    def note(self) -> 'str | None': return self.__note

    def __repr__(self) -> str: return f'{type(self).__name__}(\n    id = {self.__id},\n    payment_version = {self.__payment_version},\n    payer_name = \'{self.__payer_name}\',\n    category = \'{self.__category}\',\n    amount = {self.__amount},\n    note = \'{self.__note or ""}\',\n)'

    @staticmethod
    def validate_id(value) -> None:
        if not (type(value) in (int, type(None)) and (value is None or value > 0)): raise ValueError('ID harus berupa integer positif atau None.')
    @classmethod
    def validate_payment_version(cls, value):
        if not (type(value) == int and value > 0): raise cls.InvalidPaymentVersion('`payment_version` must be a positive integer.')
    @classmethod
    def validate_payer_name(cls, value):
        if not (type(value) == str and len(value) > 0): raise cls.InvalidPayerName('Nama pembayar harus berupa string yang tidak kosong.')
    @classmethod
    def validate_category(cls, value):
        if not (type(value) == str): raise cls.InvalidCategory('Kategory harus berupa string.')
    @classmethod
    async def validate_category_exists(cls, value):
        if await PaymentCategory.get_id_by_name(value) is None: raise cls.InexistentCategory(f'Kategori \'{value}\' tidak ada.')
    @classmethod
    def validate_amount(cls, value):
        if not (type(value) in (float, int) and value > 0): raise cls.InvalidAmount('Jumlah harus berupa angka positif.')
    @classmethod
    def validate_note(cls, value):
        if not (type(value) in (str, type(None)) and ((len(value) > 0) if type(value) == str else True)): raise cls.InvalidNote('Catatan harus berupa string yang tidak kosong atau tidak sama sekali.')

    async def insert(self, cursor: Cursor, payment_version: int) -> None:
        assert self.__id is None, 'This payment line is already created (it has an id).'
        await self.validate_category_exists(self.__category)
        async with db_connect() as conn:
            cursor = await conn.cursor()
            if self.__id is None:
                await cursor.execute(*sql.insert('zis_payment_line', payment_version=self.__payment_version, payer_name=self.__payer_name, category=await PaymentCategory.get_id_by_name(self.__category), amount=self.__amount, note=self.__note))
                self.__id = cursor.lastrowid
            await conn.commit()

    @classmethod
    async def get(cls, **kwargs) -> 'PaymentLine | None':
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*sql.select('zis_payment_line', ['id', 'username', 'name', 'password'], **kwargs))
            row = await cursor.fetchone()
            if row: return cls(row['payment_version'], row['payer_name'], str(await PaymentCategory.get_name_by_id(row['category'])), row['amount'], note=row['note'], id=row['id'])

    @classmethod
    async def get_all(cls, **kwargs) -> 'list[PaymentLine]':
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*sql.select('zis_payment_line', **kwargs))
            rows = await cursor.fetchall()
            return [cls(row['payment_version'], row['payer_name'], str(await PaymentCategory.get_name_by_id(row['category'])), row['amount'], note=row['note'], id=row['id']) for row in rows]

class PaymentCategory:
    class InvalidCategory(Exception): http_status_code = 400

    @staticmethod
    async def get_all(cursor: 'Cursor | None' = None) -> 'dict[int, str]':
        command = sql.select('zis_payment_category', ['id', 'name'])
        if isinstance(cursor, Cursor):
            await cursor.execute(*command)
            rows = await cursor.fetchall()
        else:
            async with db_connect() as conn:
                cursor = await conn.cursor()
                await cursor.execute(*command)
                rows = await cursor.fetchall()
        return {row['id']: row['name'] for row in rows}

    @staticmethod
    async def get_name_by_id(id: int, cursor: 'Cursor | None' = None) -> 'str | None':
        command = sql.select('zis_payment_category', ['name'], id=id)
        if isinstance(cursor, Cursor):
            await cursor.execute(*command)
            row = await cursor.fetchone()
        else:
            async with db_connect() as conn:
                cursor = await conn.cursor()
                await cursor.execute(*command)
                row = await cursor.fetchone()
        if row: return row['name']

    @staticmethod
    async def get_id_by_name(category: str, cursor: 'Cursor | None' = None) -> 'int | None':
        command = sql.select('zis_payment_category', ['id'], name=category.lower())
        if isinstance(cursor, Cursor):
            await cursor.execute(*command)
            row = await cursor.fetchone()
        else:
            async with db_connect() as conn:
                cursor = await conn.cursor()
                await cursor.execute(*command)
                row = await cursor.fetchone()
        if row: return row['id']

    @classmethod
    async def create(cls, category: str, cursor: 'Cursor | None' = None) -> None:
        if not (type(category) == str and 1 <= len(category) <= 64 and category.islower()): raise cls.InvalidCategory('Kategori harus berupa string dengan panjang 1-64 karakter dan hanya berisi huruf kecil.')
        select_command = sql.select('zis_payment_category', ['COUNT(*)'], name=category.lower())
        insert_command = sql.insert('zis_payment_category', name=category.lower())
        if isinstance(cursor, Cursor):
            await cursor.execute(*select_command)
            if (fetchone := await cursor.fetchone()) and fetchone[0] > 0: return
            await cursor.execute(*insert_command)
        else:
            async with db_connect() as conn:
                cursor = await conn.cursor()
                await cursor.execute(*select_command)
                if (fetchone := await cursor.fetchone()) and fetchone[0] > 0: return
                await cursor.execute(*insert_command)
                await conn.commit()

    @staticmethod
    async def delete(category: str, cursor: 'Cursor | None' = None) -> None:
        command = sql.delete('zis_payment_category', name=(category, category.lower()))
        if isinstance(cursor, Cursor): await cursor.execute(*command)
        else:
            async with db_connect() as conn:
                cursor = await conn.cursor()
                await cursor.execute(*command)
                await conn.commit()