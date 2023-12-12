import pint

u = pint.UnitRegistry()

def A_func():
    g = 2*u.feet

    for i in range(5):
        b = g * i
    return b