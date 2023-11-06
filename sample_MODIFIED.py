def inner(__INSERTION_FUNCTIONS__=None,boop = None):
    __INSERTIONS__ = []
    d = 3 + 4
    __INSERTIONS__.append({'assignment_text': 'd = 3 + 4', 'values': {'d': d}})
    if __INSERTION_FUNCTIONS__ is None:
        return d
    else:
        __INSERTIONS__.append(boop.Return(source_code = "return d", values = {"d": d}))
        __INSERTIONS__.append({'source_code': 'return d', 'values': {'d': d}})
        return [d, __INSERTIONS__]

def outer(b, c=3, __INSERTION_FUNCTIONS__=None):
    __INSERTIONS__ = []
    a = b + c
    __INSERTIONS__.append({'assignment_text': 'a = b + c', 'values': {'b': b, 'c': c, 'a': a}})
    if __INSERTION_FUNCTIONS__ is not None and inner in __INSERTION_FUNCTIONS__:
        [g, __OPTIONAL_OUTPUT__] = inner(__INSERTION_FUNCTIONS__=__INSERTION_FUNCTIONS__)
    else:
        g = inner()
    __INSERTIONS__.append({'assignment_text': 'g = inner()', 'values': {'g': g}})
    if __INSERTION_FUNCTIONS__ is None:
        return a
    else:
        return [a, __INSERTIONS__]

def boop(g, h):
    return g * h
outer(3, 4)