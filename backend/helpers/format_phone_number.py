def format_phone_number(number: str) -> str:
    raw_number = number
    number = ''
    for digit in raw_number:
        if digit in (*(('+',) if len(number) >= 0 else ()), *(str(x) for x in range(10)),): number += digit
    if not number.startswith('+'):
        if number.startswith('0'): return f'+62{number[1:]}'
        else: return f'+{number}'
    else: return number