from ..models.zis_payment import PaymentCategory, PaymentUnit
from ..helpers.log import log

async def seed() -> None:
    for category in (
        'zakat fitrah',
        'zakat maal',
        'fidyah',
        'infaq',
    ): await PaymentCategory.create(category)
    for unit in (
        'kilogram beras',
        'liter beras',
        'rupiah',
    ): await PaymentUnit.create(unit)