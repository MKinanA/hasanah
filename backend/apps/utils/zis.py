from datetime import datetime as dt
from playwright.async_api import async_playwright as pw
from ...models.user import User
from ...models.zis_payment import Payment, PaymentVersion
from ...helpers.datetime import days, months
from ..render import env as jenv

async def generate_receipt(payment: 'Payment | PaymentVersion | dict', format: 'str | None' = None, html: 'bool' = False) -> 'bytes | str':
    if isinstance(payment, Payment): payment = await payment.latest
    if isinstance(payment, PaymentVersion): payment = await payment.to_dict
    payment['units'] = []
    for line in payment['lines']:
        if not line['unit'] in payment['units']: payment['units'].append(line['unit'])
    ca = dt.fromtimestamp(payment['created_at'])
    payment['created_at'] = f'{days[(ca.weekday() + 1) % 7]}, {ca.day} {months[ca.month - 1]} {ca.year}'
    payment['created_by'] = await User.get(username=payment['created_by'])
    if payment['created_by'] is None: raise RuntimeError('Failed to fetch user from payment.created_by')
    payment['created_by'] = payment['created_by'].name
    payment['updated_by'] = await User.get(username=payment['updated_by'])
    if payment['updated_by'] is None: raise RuntimeError('Failed to fetch user from payment.updated_by')
    payment['updated_by'] = payment['updated_by'].name
    payment['totals'] = {}
    for line in payment['lines']:
        if line['unit'] not in payment['totals']: payment['totals'][line['unit']] = 0
        payment['totals'][line['unit']] += line['amount']
    html_render = jenv.get_template('pdf/zis_payment_receipt.html').render(payment, format_number=lambda x: f'{x:,}')
    if html: return html_render
    async with pw() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            try:
                await page.set_content(html_render)
                pdf = await page.pdf(format=format if isinstance(format, str) else 'A5', print_background=True)
            finally: await page.close()
        finally: await browser.close()
    return pdf