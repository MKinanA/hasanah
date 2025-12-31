from uuid import uuid4 as uuid
from time import time
from aiosqlite import IntegrityError
from .user import User
from ..helpers.db_connect import db_connect, Cursor
from ..helpers.log import log
from ..helpers import sql_commands as sql
from ..helpers.is_uuid import is_uuid
from ..helpers.repr import repr
from ..helpers.multisteps import multisteps_async

class Payment:
    class PaymentNotFound(Exception): status_code = 404
    class IncompleteOrInvalidPaymentDetails(Exception): status_code = 400
    class PaymentIsDeleted(Exception): status_code = 400
    class PaymentIsNotDeleted(Exception): status_code = 400

    def __init__(self, uuid: str, id: int):
        self.__id = id
        self.__uuid = uuid

    @property
    def id(self) -> int: return self.__id
    @property
    def uuid(self) -> str: return self.__uuid

    def __repr__(self) -> str: return repr(self)

    @staticmethod
    def validate_id(value) -> None:
        if not (type(value) == int and value > 0): raise ValueError('`id` must be a positive integer.')
    @staticmethod
    def validate_uuid(value) -> None:
        if not (type(value) == str and is_uuid(value)): raise ValueError('`uuid` must be a string of a valid UUID.')

    @classmethod
    async def get(cls, **kwargs) -> 'Payment | None':
        cls.validate_id(kwargs['id']) if 'id' in kwargs else None
        cls.validate_uuid(kwargs['uuid']) if 'uuid' in kwargs else None
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*sql.select('zis_payment', where=kwargs))
            row = await cursor.fetchone()
            if row: return cls(row['uuid'], row['id'])

    @classmethod
    async def get_all(cls, **kwargs) -> 'list[Payment]':
        cls.validate_id(kwargs['id']) if 'id' in kwargs else None
        cls.validate_uuid(kwargs['uuid']) if 'uuid' in kwargs else None
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*sql.select('zis_payment', where=kwargs))
            rows = await cursor.fetchall()
            return [cls(row['uuid'], row['id']) for row in rows]

    @classmethod
    async def query(cls, filters: 'dict | None' = None, include_deleted: bool = False, only_deleted: bool = False, sort: str = 'last_updated', limit: int = 100, offset: int = 0) -> 'list[Payment]':
        order_by = {
            'last_updated': 'pv.created_at DESC',
            'last_created': 'fv.created_at DESC',
            # 'first_updated': 'pv.created_at ASC',
            'first_created': 'fv.created_at ASC',
        }[sort]
        filter_values_parser = {
            'first_created_by': (lambda username: User.get(username=username), lambda user: user.id if user is not None else 0),
            'last_updated_by': (lambda username: User.get(username=username), lambda user: user.id if user is not None else 0),
            'created_in_timespan': lambda seconds: int(seconds),
            'updated_in_timespan': lambda seconds: int(seconds),
        }
        filters_parser = {
            'first_created_by': lambda value: (f'fv.created_by = ?', value),
            'last_updated_by': lambda value: (f'pv.created_by = ?', value),
            'created_in_timespan': lambda value: (f'fv.created_at + ? >= ?', (value, int(time()))),
            'updated_in_timespan': lambda value: (f'pv.created_at + ? >= ?', (value, int(time()))),
        }
        parsed_filters = [filters_parser[key](await multisteps_async(lambda: value, *(parser if isinstance(parser := filter_values_parser[key], (tuple, list)) else (parser,)))) for key, value in (filters or {}).items()]
        where = ' AND '.join(x for x in (
            'pv.is_deleted = 0' if not include_deleted else 'pv.is_deleted = 1' if only_deleted else None,
            *(parsed_filter[0] for parsed_filter in parsed_filters)
        ) if x is not None)
        nested_parameters = (*(parsed_filter_parameters if isinstance(parsed_filter_parameters := parsed_filter[1], (tuple, list)) else (parsed_filter_parameters,) for parsed_filter in parsed_filters),)
        command = (
            'SELECT p.* '
            'FROM zis_payment p '
            'JOIN zis_payment_version fv '
            'ON fv.payment = p.id '
            'AND fv.version = 1 '
            'JOIN ( '
                'SELECT payment, MAX(version) AS latest_version '
                'FROM zis_payment_version '
                'GROUP BY payment '
            ') lv '
            'ON lv.payment = p.id '
            'JOIN zis_payment_version pv '
            'ON pv.payment = lv.payment '
            'AND pv.version = lv.latest_version '
            f"{('WHERE ' + where + ' ') if where else ''}"
            'ORDER BY ' + order_by + ' '
            'LIMIT ? OFFSET ?',
            (*(parameter for parameters in nested_parameters for parameter in parameters), limit if (limit := int(limit)) >= 0 else 0, offset if (offset := int(offset)) >= 0 else 0)
        )

        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*command)
            rows = await cursor.fetchall()
            return [cls(row['uuid'], row['id']) for row in rows]

    @property
    async def latest(self) -> 'PaymentVersion':
        version = await self.version()
        if version is None: raise RuntimeError('Payment has no versions.')
        return version
    async def version(self, version: 'int | None' = None) -> 'PaymentVersion | None':
        async with db_connect() as conn:
            cursor = await conn.cursor()
            return await self.select_version(version, cursor)
    async def select_version(self, version: 'int | None', cursor: Cursor) -> 'PaymentVersion | None':
        if isinstance(version, int): await cursor.execute(*sql.select('zis_payment_version', where={'payment': self.__id, 'version': version}))
        else: await cursor.execute(*(lambda pair: (pair[0] + ' ORDER BY version DESC', pair[1]))(sql.select('zis_payment_version', where={'payment': self.__id})))
        row = await cursor.fetchone()
        if row:
            created_by = await User.get(id=row['created_by'])
            if created_by is None: raise RuntimeError('`created_by` user not found.')
            return PaymentVersion(payment=row['payment'], version=row['version'], payer_name=row['payer_name'], payer_number=row['payer_number'], payer_email=row['payer_email'], payer_address=row['payer_address'], note=row['note'], created_at=row['created_at'], created_by=created_by, is_deleted=bool(row['is_deleted']), id=row['id'])

    @classmethod
    async def new(cls, details: dict) -> 'Payment':
        async with db_connect() as conn:
            cursor = await conn.cursor()
            while True:
                try:
                    new_uuid = str(uuid())
                    await cursor.execute(*sql.insert('zis_payment', values={'uuid': new_uuid}))
                    break
                except IntegrityError as e:
                    if getattr(e, 'sqlite_errorname', None) != 'SQLITE_CONSTRAINT_UNIQUE': raise
            id = cursor.lastrowid
            if not isinstance(id, int): raise RuntimeError('Failed to retrieve new payment ID after insertion.')
            payment = cls(new_uuid, id)
            await payment.insert_new_version(details, cursor)
            await conn.commit()
        return payment

    async def update(self, details: dict) -> None:
        if 'is_deleted' in details: del details['is_deleted']
        async with db_connect() as conn:
            cursor = await conn.cursor()
            if (latest_version := await self.select_version(None, cursor)) is None: raise RuntimeError('Payment has no versions.')
            elif latest_version.is_deleted: raise self.PaymentIsDeleted('Can\'t update a deleted record.')
            await self.insert_new_version(details, cursor)
            await conn.commit()

    async def delete(self, by: User) -> None:
        async with db_connect() as conn:
            cursor = await conn.cursor()
            if (latest_version := await self.select_version(None, cursor)) is None: raise RuntimeError('Payment has no versions, can\'t delete a payment with no versions.')
            elif latest_version.is_deleted: raise self.PaymentIsDeleted('Can\'t delete an already deleted record.')
            details = await latest_version.to_dict
            details['created_by'] = by
            details['is_deleted'] = True
            await self.insert_new_version(details, cursor)
            await conn.commit()

    async def insert_new_version(self, details: dict, cursor: Cursor) -> None:
        try:
            version = PaymentVersion(payment=None, version=None, payer_name=details['payer_name'], payer_number=details['payer_number'] if 'payer_number' in details else None, payer_email=details['payer_email'] if 'payer_email' in details else None, payer_address=details['payer_address'], note=details['note'] if 'note' in details else None, created_at=None, created_by=details['created_by'], is_deleted=details['is_deleted'] if 'is_deleted' in details else False)
            lines = (*(PaymentLine(payment_version=None, payer_name=line['payer_name'], category=line['category'], amount=line['amount'], note=line['note'] if 'note' in line else None) for line in details['lines']),)
        except Exception as e: raise self.IncompleteOrInvalidPaymentDetails(f'Payment details are incomplete or invalid, or another error was thrown while parsing them.\n{type(e).__name__}: {e}') from e
        if not isinstance(self.__id, int): raise RuntimeError('Failed to retrieve current payment ID.')
        await version.insert(self.__id, cursor)
        if not isinstance(version.id, int): raise RuntimeError('Failed to retrieve new payment version ID after insertion.')
        for line in lines: await line.insert(version.id, cursor)

class PaymentVersion:
    class InexistentPayment(Exception): status_code = 404
    class InvalidPayment(Exception): status_code = 400
    class InvalidVersion(Exception): status_code = 400
    class InvalidPayerName(Exception): status_code = 400
    class InvalidPayerNumber(Exception): status_code = 400
    class InvalidPayerEmail(Exception): status_code = 400
    class NoPayerContact(Exception): status_code = 400
    class InvalidPayerAddress(Exception): status_code = 400
    class InvalidNote(Exception): status_code = 400
    class InvalidCreatedAt(Exception): status_code = 400
    class InvalidCreatedBy(Exception): status_code = 400
    class UnauthorizedCreatedBy(Exception): status_code = 403
    class InvalidIsDeleted(Exception): status_code = 400

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

    def __repr__(self) -> str: return repr(self)

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
        if self.__payment is not None: raise RuntimeError('Can\'t insert a payment version that already has a `payment`.')
        if self.__version is not None: raise RuntimeError('Can\'t insert a payment version that already has a `version`.')
        if self.__created_at is not None: raise RuntimeError('Can\'t insert a payment version that already has a `created_at`.')
        self.__created_at = int(time())
        await self.validate_created_by_access(self.__created_by)
        await cursor.execute(*(lambda pair: (pair[0] + ' ORDER BY version DESC', pair[1]))(sql.select('zis_payment_version', where={'payment': payment})))
        last_version = await cursor.fetchone()
        latest_version = (last_version['version'] if last_version else 0) + 1
        await cursor.execute(*sql.insert('zis_payment_version', values={'payment': payment, 'version': latest_version, 'payer_name': self.__payer_name, 'payer_number': self.__payer_number, 'payer_email': self.__payer_email, 'payer_address': self.__payer_address, 'note': self.__note, 'created_at': self.__created_at, 'created_by': self.__created_by.id, 'is_deleted': int(self.__is_deleted)}))
        self.__id = cursor.lastrowid
        self.__payment = payment
        self.__version = latest_version

    @property
    async def lines(self) -> 'list[PaymentLine]':
        async with db_connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(*sql.select('zis_payment_line', where={'payment_version': self.__id}))
            rows = await cursor.fetchall()
            return [PaymentLine(payment_version=row['payment_version'], payer_name=row['payer_name'], category=(await PaymentCategory.get_name_by_id(row['category'], cursor=cursor)) or '', amount=row['amount'], note=row['note'], id=row['id']) for row in rows]

    @property
    async def to_dict(self) -> dict: return {
        'payment': payment.uuid if (payment := await Payment.get(id=self.__payment)) else None,
        'version': self.__version,
        'payer_name': self.__payer_name,
        'payer_number': self.__payer_number,
        'payer_email': self.__payer_email,
        'payer_address': self.__payer_address,
        'note': self.__note,
        'lines': [await line.to_dict for line in await self.lines],
        'created_at': self.__created_at,
        'created_by': self.__created_by.username,
        'is_deleted': self.__is_deleted,
    }

class PaymentLine:
    class InvalidPaymentVersion(Exception): status_code = 400
    class InexistentPaymentVersion(Exception): status_code = 404
    class InvalidPayerName(Exception): status_code = 400
    class InvalidCategory(Exception): status_code = 400
    class InexistentCategory(Exception): status_code = 404
    class InvalidAmount(Exception): status_code = 400
    class InvalidNote(Exception): status_code = 400

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
        await cursor.execute(*sql.insert('zis_payment_line', values={'payment_version': payment_version, 'payer_name': self.__payer_name, 'category': await PaymentCategory.get_id_by_name(self.__category, cursor=cursor), 'amount': self.__amount, 'note': self.__note}))
        self.__id = cursor.lastrowid
        self.__payment_version = payment_version

    @property
    async def to_dict(self) -> dict: return {
        'payer_name': self.__payer_name,
        'category': self.__category,
        'amount': self.__amount,
        'note': self.__note,
    }

class PaymentCategory:
    class InvalidCategory(Exception): status_code = 400

    @staticmethod
    async def get_all(cursor: 'Cursor | None' = None) -> 'dict[int, str]':
        command = sql.select('zis_payment_category', columns=('id', 'name'))
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
        command = sql.select('zis_payment_category', columns='name', where={'id': id})
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
        command = sql.select('zis_payment_category', columns='id', where={'name': category.lower()})
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
        select_command = sql.select('zis_payment_category', columns='COUNT(*)', where={'name': category.lower()})
        insert_command = sql.insert('zis_payment_category', values={'name': category.lower()})
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
        command = sql.delete('zis_payment_category', where={'name': (category, category.lower())})
        if isinstance(cursor, Cursor): await cursor.execute(*command)
        else:
            async with db_connect() as conn:
                cursor = await conn.cursor()
                await cursor.execute(*command)
                await conn.commit()