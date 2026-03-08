from os import environ as env
from asyncio import get_running_loop
from json import dumps
from twilio.rest import Client

CLIENT = None
CONTENTS = {
    'receipt': 'HXac58814218dcdadd8c4836c4d859492f',
}

async def send(to: str, body: 'str | None' = None, content: 'str | None' = None, variables: 'dict | None' = None, media_url: 'str | list[str] | None' = None):
    global CLIENT
    client = CLIENT if isinstance(CLIENT, Client) else (CLIENT := Client(
        env['TWILIO_ACCOUNT_SID'],
        env['TWILIO_AUTH_TOKEN'],
    ))
    return await get_running_loop().run_in_executor(None, lambda: client.messages.create(
        from_=f'whatsapp:{env["WHATSAPP_SENDER_NUMBER"]}',
        to=f'whatsapp:{to}',
        **({
            'body': body,
        } if isinstance(body, str) else {}),
        **({
            'content_sid': CONTENTS[content],
            **({
                'content_variables': dumps(variables),
            } if isinstance(variables, dict) else {}),
        } if isinstance(content, str) else {}),
        **({
            'media_url': media_url if isinstance(media_url, list) else [media_url],
        } if isinstance(media_url, (str, list)) else {}),
    ))