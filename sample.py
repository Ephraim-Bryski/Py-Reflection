
def inner():
    d = 3 + 4
    return d


def outer(b, c=3):
    "NOTE this is addition"
    a = b + c
    g = inner()
    return a

def boop(g,h):
    return g*h

outer(3, 4)