def str_to_bool(value):
    result = None
    for x in (lambda x: eval(str(x).capitalize()), lambda x: bool(int(x))):
        try: result = x(value)
        except: pass
        if type(result) == bool: return result
    return bool(value)