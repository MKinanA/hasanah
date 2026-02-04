from io import BytesIO
from time import time
from datetime import datetime
from random import Random
from colorsys import hls_to_rgb
from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse, StreamingResponse
from openpyxl import Workbook, styles as wstyles
from ...models.user import User, Access
from ...models.zis_payment import Payment, PaymentCategory, PaymentUnit
from ..dependencies import auth, NoAuthToken, UserSessionNotFound
from ..render import render

router = APIRouter()
payments = APIRouter()

@router.get('')
async def root(): return RedirectResponse(url=f'/{__name__.split(".")[-1]}/payments', status_code=302)

@payments.get('')
async def payments_index(request: Request):
    try:
        user = await auth(request)
        await user.require_access(Access.ZIS_PAYMENT_READ)
    except (NoAuthToken, UserSessionNotFound): return RedirectResponse(url='/login', status_code=302)
    except Access.AccessDenied: return RedirectResponse(url='/home', status_code=302)
    return await render('pages/zis/payments', {'user': user, 'payments': [(await (await payment.latest).to_dict) for payment in await Payment.query()]}, expose='payments')

@payments.get('/export-xlsx')
async def payments_xlsx(request: Request):
    try:
        user = await auth(request)
        await user.require_access(Access.ZIS_PAYMENT_READ)
    except (NoAuthToken, UserSessionNotFound): return RedirectResponse(url='/login', status_code=302)
    except Access.AccessDenied: return RedirectResponse(url='/home', status_code=302)
    wb = Workbook()
    ws = wb.active
    if ws is None: raise RuntimeError('Failed to get active sheet of workbook object (using openpyxl).')
    ws.title = 'Pembayaran Zakat'
    ws.append((
        'Nomor Zakat',
        'Nomor Transaksi',
        'Nama',
        'Alamat',
        'Kategori',
        None,
        None,
        None,
        'Beras',
        None,
        'Uang',
        'Admin',
        'Edit',
        'UUID',
    ))
    for start, end in ((5, 8), (9, 10)): ws.merge_cells(
        start_row=ws.max_row,
        start_column=start,
        end_row=ws.max_row,
        end_column=end,
    )
    ws.append((
        *(None,) * 4,
        'Fitrah',
        'Maal',
        'Fidyah',
        'Infaq',
        'Kilogram',
        'Liter',
    ))
    for col in (*range(1, 5), *range(11, 15)): ws.merge_cells(
        start_row=ws.max_row - 1,
        start_column=col,
        end_row=ws.max_row,
        end_column=col,
    )
    counter = 0
    users = {}
    for payment in (await Payment.query())[::-1]:
        counter += 1
        payment = await (await payment.latest).to_dict
        created_by = users[username] if (username := payment['created_by']) in users else (await User.get(username=username))
        if username not in users: users[username] = created_by
        updated_by = users[username] if (username := payment['updated_by']) in users else (await User.get(username=username))
        if username not in users: users[username] = updated_by
        ws.append(())
        ws.merge_cells(
            start_row=ws.max_row+1,
            start_column=1,
            end_row=ws.max_row+1,
            end_column=14,
        )
        ws.append((*(f'\'x' if isinstance(x, str) and x.startswith('=') else x for x in (
            counter,
            1,
            payment['lines'][0]['payer_name'],
            payment['payer_address'],
            '✓' if payment['lines'][0]['category'] == 'zakat fitrah' else None,
            '✓' if payment['lines'][0]['category'] == 'zakat maal' else None,
            '✓' if payment['lines'][0]['category'] == 'fidyah' else None,
            '✓' if payment['lines'][0]['category'] == 'infaq' else None,
            payment['lines'][0]['amount'] if payment['lines'][0]['unit'] == 'kilogram beras' else None,
            payment['lines'][0]['amount'] if payment['lines'][0]['unit'] == 'liter beras' else None,
            payment['lines'][0]['amount'] if payment['lines'][0]['unit'] == 'rupiah' else None,
            f'{created_by.name} ({created_by.username})' if created_by is not None else '[Gagal mendapatkan informasi user]',
            f'{updated_by.name} ({updated_by.username})' if updated_by is not None else '[Gagal mendapatkan informasi user]',
            payment['payment'],
        )),))
        ws.cell(
            row=ws.max_row,
            column=11,
        ).number_format = '[$Rp-421]#,##0'
        for col in (
            {'col': 12, 'username': created_by.username if created_by is not None else ''},
            {'col': 13, 'username': updated_by.username if updated_by is not None else ''},
        ): ws.cell(
            row=ws.max_row,
            column=col['col'],
        ).fill = wstyles.PatternFill(
            start_color=(lambda x: f'{round((c := hls_to_rgb(Random(x).randint(0, 255) / 255, 0.5, 1))[0] * 255):02X}{round(c[1] * 255):02X}{round(c[2] * 255):02X}')(col['username']),
            fill_type='solid',
        )
        line_counter = 1
        for line in payment['lines'][1:]:
            line_counter += 1
            ws.append((*(f'\'x' if isinstance(x, str) and x.startswith('=') else x for x in (
                None,
                line_counter,
                line['payer_name'],
                None,
                '✓' if line['category'] == 'zakat fitrah' else None,
                '✓' if line['category'] == 'zakat maal' else None,
                '✓' if line['category'] == 'fidyah' else None,
                '✓' if line['category'] == 'infaq' else None,
                line['amount'] if line['unit'] == 'kilogram beras' else None,
                line['amount'] if line['unit'] == 'liter beras' else None,
                line['amount'] if line['unit'] == 'rupiah' else None,
            )),))
            ws.cell(
                row=ws.max_row,
                column=11,
            ).number_format = '[$Rp-421]#,##0'
        for col in (1, 4, *range(12, 15)):
            if len(payment['lines']) > 1: ws.merge_cells(
                start_row=ws.max_row - len(payment['lines']) + 1,
                start_column=col,
                end_row=ws.max_row,
                end_column=col,
            )
        for col in 'ABCDEFGHIJKLMN': ws.column_dimensions[col].auto_size = True
    wb.save(buffer := BytesIO())
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': f'attachment; filename=Export_Pembayaran_ZIS_{int(time())}.xlsx'}
    )

@payments.get('/new')
async def payment_new(request: Request, response: Response):
    try:
        user = await auth(request)
        await user.require_access(Access.ZIS_PAYMENT_READ, Access.ZIS_PAYMENT_WRITE)
    except (NoAuthToken, UserSessionNotFound): return RedirectResponse(url='/login', status_code=302)
    except Access.AccessDenied: return RedirectResponse(url=f'/payments' if user.has_access(Access.ZIS_PAYMENT_READ) else '/home', status_code=302)
    return await render('pages/zis/payments/new', {'user': user, 'categories': (*({'value': category, 'name': category.capitalize()} for id, category in (await PaymentCategory.get_all()).items()),), 'units': (*({'value': unit, 'name': unit.capitalize()} for id, unit in (await PaymentUnit.get_all()).items()),)})

@payments.get('/{uuid}')
async def payment(request: Request, response: Response, uuid: str):
    try:
        user = await auth(request)
        await user.require_access(Access.ZIS_PAYMENT_READ)
    except (NoAuthToken, UserSessionNotFound): return RedirectResponse(url='/login', status_code=302)
    except Access.AccessDenied: return RedirectResponse(url='/home', status_code=302)
    payment = await Payment.get(uuid=uuid)
    if payment is None: return await render('pages/error', {'code': '404', 'error': 'Pembayaran Tidak Ditemukan', 'user': user}, status_code=404)
    return await render('pages/zis/payments/show', {'user': user, 'payment': await (await payment.latest).to_dict}, expose='payment')

@payments.get('/{uuid}/edit')
async def payment_edit(request: Request, response: Response, uuid: str):
    try:
        user = await auth(request)
        await user.require_access(Access.ZIS_PAYMENT_READ, Access.ZIS_PAYMENT_WRITE)
    except (NoAuthToken, UserSessionNotFound): return RedirectResponse(url='/login', status_code=302)
    except Access.AccessDenied: return RedirectResponse(url=f'/payments/{uuid}' if user.has_access(Access.ZIS_PAYMENT_READ) else '/home', status_code=302)
    payment = await Payment.get(uuid=uuid)
    if payment is None: return await render('pages/error', {'code': '404', 'error': 'Pembayaran Tidak Ditemukan', 'user': user}, status_code=404)
    return await render('pages/zis/payments/edit', {'user': user, 'payment': await (await payment.latest).to_dict, 'categories': (*({'value': category, 'name': category.capitalize()} for id, category in (await PaymentCategory.get_all()).items()),), 'units': (*({'value': unit, 'name': unit.capitalize()} for id, unit in (await PaymentUnit.get_all()).items()),)}, expose='payment')

router.include_router(payments, prefix='/payments')