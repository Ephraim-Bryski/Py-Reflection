def inner(g, __INSERTION_FUNCTIONS__=None):
    __INSERTIONS__ = []
    d = g + 4
    __INSERTIONS__.append({'source_code': 'd = g + 4', 'values': {'d': d, 'g': g}})
    if __INSERTION_FUNCTIONS__ is None:
        return d
    else:
        return [d, __INSERTIONS__]

def outer(b, c=3):
    """NOTE this is addition"""
    a = b + c
    g = inner()
    return a

def boop(g, h):
    return g * h