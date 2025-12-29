attr_types_to_include = (int, float, str, bool, type(None))
def repr(obj: object, include_attr_names: 'tuple | None' = None, include_attr_types: 'tuple | None' = None, exclude_attr_names: 'tuple | None' = None, exclude_attr_types: 'tuple | None' = None, indent: 'int | None' = 4) -> str:
    include_attr_types = include_attr_types or attr_types_to_include
    attrs = {}
    for attr in dir(obj):
        try: value = getattr(obj, attr)
        except AttributeError: continue
        if (isinstance(value, include_attr_types) or (attr in include_attr_names if isinstance(include_attr_names, tuple) else True)) and not ((isinstance(value, exclude_attr_types) if isinstance(exclude_attr_types, tuple) else False) or (attr in exclude_attr_names if isinstance(exclude_attr_names, tuple) else False) or attr.startswith('_')): attrs[attr] = value
    repr = f'{type(obj).__name__}('
    for attr, value in attrs.items(): repr += ('' if indent is None else '\n') + (' ' * (indent or 0)) + attr + ' = ' + ('\'' if isinstance(value, str) else '') + str(value) + ('\'' if isinstance(value, str) else '') + ','
    repr += '\n)'
    return repr