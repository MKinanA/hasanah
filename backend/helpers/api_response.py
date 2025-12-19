def api_response(type: str, elaboration: str, message: str, **data) -> dict:
    assert type in ('success', 'error'), 'Invalid type'
    return {
        'type': type,
        type: elaboration,
        'message': message,
        **data,
    }