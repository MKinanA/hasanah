attr_types_to_include = (int, float, str, bool, type(None))
def repr(obj: object, indent: 'int | None' = 4) -> str:
    attrs = {}
    for attr in dir(obj):
        try: value = getattr(obj, attr)
        except AttributeError: continue
        if isinstance(value, attr_types_to_include) and not attr.startswith('_'): attrs[attr] = value
    repr = f'{type(obj).__name__}('
    for attr, value in attrs.items(): repr += ('' if indent is None else '\n') + (' ' * (indent or 0)) + attr + ' = ' + ('\'' if isinstance(value, str) else '') + str(value) + ('\'' if isinstance(value, str) else '') + ','
    repr += '\n)'
    return repr