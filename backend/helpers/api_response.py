def api_response(type: str, elaboration: str, message: str, **data) -> dict:
    if type not in ('success', 'error'): raise ValueError('Invalid type')
    return {
        'type': type,
        type: elaboration,
        'message': message,
        **data,
    }