from ..models.user import User
from ..helpers.db_connect import db_connect, Cursor
from ..helpers.log import log
from ..helpers import sql_commands as sql

class Payment:
    class PaymentNotFound(Exception): http_status_code = 404

    def __init__(self): pass

class PaymentVersion:
    class InexistentPayment(Exception): http_status_code = 404
    class InvalidPayment(Exception): http_status_code = 400
    class InvalidVersion(Exception): http_status_code = 400
    class InvalidPayerName(Exception): http_status_code = 400
    class InvalidPayerNumber(Exception): http_status_code = 400
    class InvalidPayerEmail(Exception): http_status_code = 400
    class NoPayerContact(Exception): http_status_code = 400
    class InvalidPayerAddress(Exception): http_status_code = 400
    class InvalidNote(Exception): http_status_code = 400
    class InvalidCreatedAt(Exception): http_status_code = 400
    class InvalidCreatedBy(Exception): http_status_code = 400
    class UnauthorizedCreatedBy(Exception): http_status_code = 403
    class InvalidIsDeleted(Exception): http_status_code = 400

    def __init__(self, payment: 'int | None', version: 'int | None', payer_name: str, payer_number: 'str | None', payer_email: 'str | None', payer_address: str, note: 'str | None', created_at: 'int | None', created_by: User, is_deleted: 'bool | int' = False, id: 'int | None' = None):
        self.validate_id(id)
        self.validate_payment(payment)
        self.validate_version(version)
        self.validate_payer_name(payer_name)
        self.validate_payer_number(payer_number)
        self.validate_payer_email(payer_email)
        self.validate_payer_contact_exists(payer_number, payer_email)
        self.validate_payer_address(payer_address)
        self.validate_note(note)
        self.validate_created_at(created_at)
        self.validate_created_by(created_by)
        self.validate_is_deleted(is_deleted)
        self.__id = id
        self.__payment = payment
        self.__version = version
        self.__payer_name = payer_name
        self.__payer_number = payer_number
        self.__payer_email = payer_email
        self.__payer_address = payer_address
        self.__note = note
        self.__created_at = created_at
        self.__created_by = created_by
        self.__is_deleted = is_deleted

    @property
    def id(self) -> 'int | None': return self.__id
    @property
    def payment(self) -> 'int | None': return self.__payment
    @property
    def version(self) -> 'int | None': return self.__version
    @property
    def payer_name(self) -> str: return self.__payer_name
    @property
    def payer_number(self) -> 'str | None': return self.__payer_number
    @property
    def payer_email(self) -> 'str | None': return self.__payer_email
    @property
    def payer_address(self) -> str: return self.__payer_address
    @property
    def note(self) -> 'str | None': return self.__note
    @property
    def created_at(self) -> 'int | None': return self.__created_at
    @property
    def created_by(self) -> User: return self.__created_by
    @property
    def is_deleted(self) -> bool: return bool(self.__is_deleted)

    # def __repr__(self) -> str: pass

    @staticmethod
    def validate_id(value) -> None:
        if not (type(value) in (int, type(None)) and (value is None or value > 0)): raise ValueError('`id` must be a positive integer or None.')
    @classmethod
    def validate_payment(cls, value):
        if not (type(value) in (int, type(None)) and (value is None or value > 0)): raise cls.InvalidPayment('`payment` must be a positive integer or None.')
    @classmethod
    def validate_version(cls, value):
        if not (type(value) in (int, type(None)) and (value is None or value > 0)): raise cls.InvalidVersion('`version` must be a positive integer or None.')
    @classmethod
    def validate_payer_name(cls, value):
        if not (type(value) == str and len(value) > 0): raise cls.InvalidPayerName('Nama pembayar harus berupa string yang tidak kosong.')
    @classmethod
    def validate_payer_number(cls, value):
        if not (type(value) in (str, type(None)) and ((len(value) > 0) if type(value) == str else True)): raise cls.InvalidPayerNumber('Nomor pembayar harus berupa string yang tidak kosong atau tidak sama sekali.')
    @classmethod
    def validate_payer_email(cls, value):
        if not (type(value) in (str, type(None)) and ((len(value) > 0) if type(value) == str else True)): raise cls.InvalidPayerEmail('Email pembayar harus berupa string yang tidak kosong atau tidak sama sekali.')
    @classmethod
    def validate_payer_contact_exists(cls, number, email):
        if not (number is not None or email is not None): raise cls.NoPayerContact('Setidaknya salah satu dari nomor atau email pembayar harus diisi.')
    @classmethod
    def validate_payer_address(cls, value):
        if not (type(value) == str and len(value) > 0): raise cls.InvalidPayerAddress('Alamat pembayar harus berupa string yang tidak kosong.')
    @classmethod
    def validate_note(cls, value):
        if not (type(value) in (str, type(None)) and ((len(value) > 0) if type(value) == str else True)): raise cls.InvalidNote('Catatan harus berupa string yang tidak kosong atau tidak sama sekali.')
    @classmethod
    def validate_created_at(cls, value):
        if not (type(value) in (int, type(None)) and (value is None or value > 0)): raise cls.InvalidCreatedAt('`created_at` must be a positive integer (or None for automatic on insert).')
    @classmethod
    def validate_created_by(cls, value):
        if not (isinstance(value, User)): raise cls.InvalidCreatedBy('`created_by` must be a User.')
    @classmethod
    async def validate_created_by_access(cls, created_by: User):
        if not 'zis_payment_create' in (await created_by.accesses): raise cls.UnauthorizedCreatedBy('`created_by` user doesn\'t have the required access.')
    @classmethod
    def validate_is_deleted(cls, value):
        if not (type(value) in (int, bool) and (type(value) == bool or value in (0, 1))): raise cls.InvalidIsDeleted('`is_deleted` must be a boolean (or 0 and 1 integer).')

    async def insert(self, payment: int, cursor: Cursor) -> None:
        if self.__id is not None: raise RuntimeError('Can\'t insert a payment version that already has an `id`.')
        if self.__payment is not None: raise RuntimeError('Can\'t insert a payment version that already has an `payment`.')
        if self.__version is not None: raise RuntimeError('Can\'t insert a payment version that already has an `version`.')
        await self.validate_created_by_access(self.__created_by)
        latest_version = 1 # TODO: Fetch latest version from DB
        await cursor.execute(*sql.insert('zis_payment_version', payment=payment, version=latest_version, payer_name=self.__payer_name, payer_number=self.__payer_number, payer_email=self.__payer_email, payer_address=self.__payer_address, note=self.__note, created_at=self.__created_at, created_by=self.__created_by.id, is_deleted=self.__is_deleted))
        self.__id = cursor.lastrowid
        self.__payment = payment
        self.__version = latest_version

class PaymentLine:
    class InvalidPaymentVersion(Exception): http_status_code = 400
    class InexistentPaymentVersion(Exception): http_status_code = 404
    class InvalidPayerName(Exception): http_status_code = 400
    class InvalidCategory(Exception): http_status_code = 400
    class InexistentCategory(Exception): http_status_code = 404
    class InvalidAmount(Exception): http_status_code = 400
    class InvalidNote(Exception): http_status_code = 400

    def __init__(self, payment_version: 'int | None', payer_name: str, category: str, amount: 'float | int', note: 'str | None' = None, id: 'int | None' = None):
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
    def payment_version(self) -> 'int | None': return self.__payment_version
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
        if not (type(value) in (int, type(None)) and (value is None or value > 0)): raise ValueError('`id` must be a positive integer or None.')
    @classmethod
    def validate_payment_version(cls, value):
        if not (type(value) in (int, type(None)) and (value is None or value > 0)): raise cls.InvalidPaymentVersion('`payment_version` must be a positive integer or None.')
    @classmethod
    def validate_payer_name(cls, value):
        if not (type(value) == str and len(value) > 0): raise cls.InvalidPayerName('Nama pembayar harus berupa string yang tidak kosong.')
    @classmethod
    def validate_category(cls, value):
        if not (type(value) == str): raise cls.InvalidCategory('Kategory harus berupa string.')
    @classmethod
    async def validate_category_exists(cls, category: str, cursor: 'Cursor'):
        if await PaymentCategory.get_id_by_name(category, cursor=cursor) is None: raise cls.InexistentCategory(f'Kategori \'{category}\' tidak ada.')
    @classmethod
    def validate_amount(cls, value):
        if not (type(value) in (float, int) and value > 0): raise cls.InvalidAmount('Jumlah harus berupa angka positif.')
    @classmethod
    def validate_note(cls, value):
        if not (type(value) in (str, type(None)) and ((len(value) > 0) if type(value) == str else True)): raise cls.InvalidNote('Catatan harus berupa string yang tidak kosong atau tidak sama sekali.')

    async def insert(self, payment_version: int, cursor: Cursor) -> None:
        if self.__id is not None: raise RuntimeError('Can\'t insert a payment line that already has an `id`.')
        if self.__payment_version is not None: raise RuntimeError('Can\'t insert a payment line that already has an `payment_version`.')
        await self.validate_category_exists(self.__category, cursor=cursor)
        await cursor.execute(*sql.insert('zis_payment_line', payment_version=payment_version, payer_name=self.__payer_name, category=await PaymentCategory.get_id_by_name(self.__category, cursor=cursor), amount=self.__amount, note=self.__note))
        self.__id = cursor.lastrowid
        self.__payment_version = payment_version

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