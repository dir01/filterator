def resolve_value(obj, name):
    for attr in name.split('__'):
        obj = getattr(obj, attr)
        if obj is None:
            return None
        if hasattr(obj, '__call__'):
            return obj()
    return obj
