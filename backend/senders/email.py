from os import environ as env
from email.message import EmailMessage
from aiosmtplib import send as send_email

EMAIL_SENDER_ADDRESS = None
SMTP_SERVER = None
SMTP_PORT = None
SMTP_USERNAME = None
SMTP_PASSWORD = None
CONTENTS = {
    'receipt': {
        'subject': 'Tanda Terima Pembayaran Zakat, Infaq, Shadaqah - Masjid Al-Hasanah',
        'content': 'Assalamu\'alaikum Bapak/Ibu {name}, berikut adalah tanda terima pembayaran anda, jazakumullah khairan.'
    }
}

async def send(to: str, content: 'dict | str', variables: 'dict | None' = None, files: 'tuple[dict] | list[dict] | None' = None):
    global EMAIL_SENDER_ADDRESS, SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD

    if not isinstance(content, dict): content = CONTENTS[content]
    message = EmailMessage()
    message['From'], message['To'], message['Subject'] = (
        (EMAIL_SENDER_ADDRESS or (EMAIL_SENDER_ADDRESS := env['EMAIL_SENDER_ADDRESS'])),
        to,
        content['subject'],
    )

    message.set_content(str(content['content']).format_map(variables or {}))
    if 'html' in content: message.add_alternative(str(content['html']).format_map(variables or {}), subtype='html')

    for file in files or (): message.add_attachment(
        file['content'],
        maintype=str(file['mimetype']).split('/')[0],
        subtype=str(file['mimetype']).split('/')[-1],
        filename=file['name'],
    )

    return await send_email(
        message,
        hostname=(SMTP_SERVER or (SMTP_SERVER := env['SMTP_SERVER'])),
        port=int(SMTP_PORT or (SMTP_PORT := env['SMTP_PORT'])),
        start_tls=True,
        username=(SMTP_USERNAME or (SMTP_USERNAME := env['SMTP_USERNAME'])),
        password=(SMTP_PASSWORD or (SMTP_PASSWORD := env['SMTP_PASSWORD'])),
    )